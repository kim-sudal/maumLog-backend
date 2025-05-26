from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from datetime import datetime
import asyncio
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api-gateway")

app = FastAPI(title="API Gateway")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 환경변수 설정
DISCOVERY_URL = os.getenv("DISCOVERY_URL", "http://discovery:8761")
SERVICE_UPDATE_INTERVAL = int(os.getenv("SERVICE_UPDATE_INTERVAL", "30"))

# 서비스 라우트 맵
service_routes = {}

async def update_services():
    """디스커버리 서비스에서 서비스 목록 갱신"""
    global service_routes
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{DISCOVERY_URL}/services")
            response.raise_for_status()
            services_data = response.json()
            
            new_routes = {}
            for service_name, instances in services_data.items():
                # UP 상태인 인스턴스만 선택
                active_instances = [
                    inst for inst in instances 
                    if inst.get("status") == "UP"
                ]
                
                if active_instances:
                    # 첫 번째 활성 인스턴스 사용
                    instance = active_instances[0]
                    instance_url = instance.get("url")
                    
                    if instance_url:
                        new_routes[service_name] = instance_url
            
            service_routes = new_routes
            logger.info(f"Services updated: {list(service_routes.keys())}")
            
    except Exception as e:
        logger.error(f"Failed to update services: {e}")

@app.on_event("startup")
async def startup_event():
    """앱 시작 시 초기화"""
    # 시작시에는 서비스 갱신만 시도 (실패해도 상관없음)
    try:
        await update_services()
    except:
        logger.info("Initial service update failed - will retry automatically")
    
    # 주기적 갱신 시작
    asyncio.create_task(service_updater_loop())

async def service_updater_loop():
    """주기적으로 서비스 목록 갱신"""
    while True:
        await asyncio.sleep(SERVICE_UPDATE_INTERVAL)
        await update_services()

@app.get("/")
async def root():
    return {
        "message": "API Gateway is running",
        "timestamp": datetime.now().isoformat(),
        "available_services": list(service_routes.keys()),
        "service_routes": service_routes
    }

# 모든 HTTP 메서드를 처리하는 라우트
@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gateway_with_path(service: str, path: str, request: Request):
    return await route_request(service, path, request)

@app.api_route("/{service}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gateway_root(service: str, request: Request):
    return await route_request(service, "", request)

async def route_request(service: str, path: str, request: Request):
    """요청 라우팅 처리 - 단순하고 직관적으로"""
    
    # 1. 서비스 존재 확인
    if service not in service_routes:
        # 실시간으로 서비스 목록 업데이트 시도
        await update_services()
        
        # 여전히 없으면 404
        if service not in service_routes:
            raise HTTPException(
                status_code=404, 
                detail=f"Service '{service}' not found in discovery"
            )
    
    # 2. 대상 URL 구성
    base_url = service_routes[service].rstrip("/")
    target_url = f"{base_url}/{path}" if path else base_url
    
    # 3. 헤더 준비 (호스트 관련 헤더만 제외)
    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in ["host", "content-length"]
    }
    
    # 4. 요청 전달
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 요청 바디 읽기 (POST, PUT, PATCH만)
            body = None
            if request.method in ["POST", "PUT", "PATCH"]:
                body = await request.body()
            
            # 실제 요청 전송
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=dict(request.query_params)
            )
            
            # 5. 응답 반환
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
    except httpx.ConnectError:
        # 연결 실패 - 서비스가 다운되었을 수 있음
        raise HTTPException(
            status_code=503, 
            detail=f"Service '{service}' is not reachable"
        )
    except httpx.TimeoutException:
        # 타임아웃
        raise HTTPException(
            status_code=504, 
            detail=f"Service '{service}' timeout"
        )
    except Exception as e:
        # 기타 오류
        logger.error(f"Unexpected error routing to {service}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Gateway internal error"
        )

@app.get("/health")
@app.get("/actuator/health")
async def health_check():
    """게이트웨이 헬스체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "available_services": list(service_routes.keys())
    }

@app.get("/services")
async def list_services():
    """등록된 서비스 목록"""
    return {
        "services": list(service_routes.keys()),
        "routes": service_routes
    }

@app.post("/refresh")
async def refresh_services():
    """서비스 목록 수동 갱신"""
    await update_services()
    return {
        "message": "Services refreshed",
        "available_services": list(service_routes.keys())
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("SERVICE_PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)