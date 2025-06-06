from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import Dict, Any, List
import uvicorn
import os
import asyncio

app = FastAPI(title="Discovery Service")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 서비스 레지스트리
service_registry: Dict[str, List[Dict[str, Any]]] = {}

# 설정
HEARTBEAT_TIMEOUT = timedelta(seconds=60)
SERVICE_CHECK_INTERVAL = 30

@app.get("/")
async def root():
    return {
        "message": "Discovery Service is running",
        "registered_services": len(service_registry),
        "services": list(service_registry.keys())
    }

@app.post("/register")
async def register_service(service_info: dict):
    service_name = service_info.get("name")
    service_host = service_info.get("host", "localhost")
    service_port = service_info.get("port")
    
    if not service_name or not service_port:
        raise HTTPException(status_code=400, detail="Missing service name or port")
    
    # 도커 컨테이너명을 호스트로 사용 (동일 네트워크)
    service_url = f"http://{service_name}:{service_port}"
    instance_id = service_info.get("instanceId", f"{service_name}-{int(datetime.utcnow().timestamp())}")
    
    instance = {
        "instanceId": instance_id,
        "url": service_url,
        "hostName": service_name,  # 도커 컨테이너명
        "port": service_port,
        "status": "UP",
        "registered_at": datetime.utcnow().isoformat(),
        "last_heartbeat": datetime.utcnow(),
        "healthCheckUrl": f"{service_url}/health"
    }
    
    if service_name not in service_registry:
        service_registry[service_name] = []
    
    # 기존 인스턴스 업데이트 또는 새로 추가
    for i, existing in enumerate(service_registry[service_name]):
        if existing.get("instanceId") == instance_id:
            service_registry[service_name][i] = instance
            return {"message": f"Service '{service_name}' updated", "instanceId": instance_id}
    
    service_registry[service_name].append(instance)
    print(f"서비스 등록: {service_name}:{service_port}")
    
    return {"message": f"Service '{service_name}' registered", "instanceId": instance_id}

@app.put("/heartbeat/{service_name}")
async def heartbeat(service_name: str, instance_id: str = None):
    if service_name not in service_registry:
        raise HTTPException(status_code=404, detail="Service not found")
    
    now = datetime.utcnow()
    
    for instance in service_registry[service_name]:
        if not instance_id or instance.get("instanceId") == instance_id:
            instance["last_heartbeat"] = now
            instance["status"] = "UP"
    
    return {"message": f"Heartbeat received: {service_name}"}

@app.get("/services")
async def get_all_services():
    result = {}
    for service_name, instances in service_registry.items():
        result[service_name] = [
            {**instance, "last_heartbeat": instance["last_heartbeat"].isoformat()}
            for instance in instances
        ]
    return result

@app.get("/services/{service_name}")
async def get_service(service_name: str):
    if service_name not in service_registry:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # UP 상태 인스턴스만 반환
    active_instances = [
        {**instance, "last_heartbeat": instance["last_heartbeat"].isoformat()}
        for instance in service_registry[service_name]
        if instance["status"] == "UP"
    ]
    
    if not active_instances:
        raise HTTPException(status_code=503, detail="No active instances available")
    
    return {
        "service": service_name,
        "instances": active_instances,
        "instance_count": len(active_instances)
    }

@app.delete("/services/{service_name}")
async def deregister_service(service_name: str, instance_id: str = None):
    if service_name not in service_registry:
        raise HTTPException(status_code=404, detail="Service not found")
    
    if instance_id:
        instances = service_registry[service_name]
        for i, instance in enumerate(instances):
            if instance.get("instanceId") == instance_id:
                service_registry[service_name].pop(i)
                if not service_registry[service_name]:
                    del service_registry[service_name]
                return {"message": f"Instance '{instance_id}' deregistered"}
        raise HTTPException(status_code=404, detail="Instance not found")
    
    del service_registry[service_name]
    return {"message": f"Service '{service_name}' deregistered"}

@app.get("/health")
@app.get("/actuator/health")  # 도커 헬스체크용
async def health_check():
    return {
        "status": "healthy",
        "registered_services": len(service_registry),
        "timestamp": datetime.utcnow().isoformat()
    }

# 백그라운드 상태 체크
async def update_service_status():
    while True:
        now = datetime.utcnow()
        for service_name, instances in service_registry.items():
            for instance in instances:
                last_beat = instance["last_heartbeat"]
                if isinstance(last_beat, str):
                    last_beat = datetime.fromisoformat(last_beat)
                
                if now - last_beat > HEARTBEAT_TIMEOUT:
                    instance["status"] = "DOWN"
                else:
                    instance["status"] = "UP"
        
        await asyncio.sleep(SERVICE_CHECK_INTERVAL)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(update_service_status())

if __name__ == "__main__":
    # 환경변수에서 포트 읽기 (기본값: 8762)
    port = int(os.getenv("SERVICE_PORT", 8762))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False
    )