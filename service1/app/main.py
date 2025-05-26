# main.py (라우터 등록 부분 수정 필요)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn
import requests
import time
import threading
from datetime import datetime
from contextlib import asynccontextmanager

# 환경변수 로딩 - 최상단에 추가
from dotenv import load_dotenv
load_dotenv()

# 코어 모듈 임포트
from app.database import engine, Base, get_db

# 라우터 임포트 - 수정됨
from app.emotion_diary.router import router as diary_router
from app.user.router import router as user_router

# 서비스 정보 (환경변수에서 읽기)
SERVICE_NAME = os.getenv("SERVICE_NAME", "service1")
SERVICE_HOST = os.getenv("SERVICE_HOST", "0.0.0.0")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8001"))  # 도커 컴포즈에서 8001로 고정

# 도커 환경에서는 컨테이너명을 사용
INSTANCE_ID = f"{SERVICE_NAME}-{os.getenv('HOSTNAME', str(int(time.time())))}"

# 디스커버리 서비스 연결
DISCOVERY_URL = os.getenv("DISCOVERY_SERVICE_URL", "http://discovery:8761")

# 서비스 등록 정보
def get_service_info():
    return {
        "name": SERVICE_NAME,
        "host": SERVICE_NAME,  # 도커 컨테이너명 사용
        "port": SERVICE_PORT,
        "instanceId": INSTANCE_ID
    }

# 디스커버리 서비스 등록
def register_service():
    max_retries = 5
    for attempt in range(max_retries):
        try:
            service_info = get_service_info()
            response = requests.post(
                f"{DISCOVERY_URL}/register",
                json=service_info,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Service registered: {SERVICE_NAME}:{SERVICE_PORT}")
                return True
            else:
                print(f"❌ Registration failed: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Registration attempt {attempt + 1} failed: {e}")
            
        if attempt < max_retries - 1:
            time.sleep(5)  # 5초 대기 후 재시도
    
    print("❌ All registration attempts failed")
    return False

# 하트비트 전송
def send_heartbeat():
    try:
        response = requests.put(
            f"{DISCOVERY_URL}/heartbeat/{SERVICE_NAME}",
            params={"instance_id": INSTANCE_ID},
            timeout=5
        )
        return response.status_code == 200
    except:
        return False

# 하트비트 백그라운드 태스크
def heartbeat_worker():
    while True:
        if send_heartbeat():
            print(f"💓 Heartbeat sent: {SERVICE_NAME}")
        else:
            print(f"💔 Heartbeat failed: {SERVICE_NAME}")
        time.sleep(30)  # 30초마다 하트비트

# 서비스 등록 해제
def deregister_service():
    try:
        response = requests.delete(
            f"{DISCOVERY_URL}/services/{SERVICE_NAME}",
            params={"instance_id": INSTANCE_ID},
            timeout=5
        )
        if response.status_code == 200:
            print(f"✅ Service deregistered: {SERVICE_NAME}")
            return True
    except Exception as e:
        print(f"❌ Deregistration failed: {e}")
    return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시
    print(f"🚀 Starting {SERVICE_NAME} on {SERVICE_HOST}:{SERVICE_PORT}")
    print(f"🔍 Discovery URL: {DISCOVERY_URL}")
    
    # 환경변수 확인 (디버깅용)
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print(f"✅ OpenAI API Key loaded (length: {len(openai_key)})")
    else:
        print("❌ OpenAI API Key not found in environment variables")
    
    # 데이터베이스 초기화
    Base.metadata.create_all(bind=engine)
    
    # 서비스 등록 및 하트비트 시작
    if register_service():
        heartbeat_thread = threading.Thread(target=heartbeat_worker, daemon=True)
        heartbeat_thread.start()
    
    yield
    
    # 종료 시
    print(f"🛑 Stopping {SERVICE_NAME}")
    deregister_service()

# FastAPI 앱 생성
app = FastAPI(
    title=f"{SERVICE_NAME} API",
    description="Microservice API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록 - 수정됨
app.include_router(diary_router)
app.include_router(user_router)

@app.get("/")
def read_root():
    return {
        "message": f"Welcome to {SERVICE_NAME}",
        "service": SERVICE_NAME,
        "instance": INSTANCE_ID,
        "port": SERVICE_PORT
    }


@app.get("/info")
def service_info():
    return {
        "service": SERVICE_NAME,
        "instance": INSTANCE_ID,
        "host": SERVICE_HOST,
        "port": SERVICE_PORT,
        "discovery_url": DISCOVERY_URL
    }

if __name__ == "__main__":
    print(f"🚀 Starting uvicorn on {SERVICE_HOST}:{SERVICE_PORT}")
    uvicorn.run(
        app,
        host=SERVICE_HOST,
        port=SERVICE_PORT,
        reload=False
    )