from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import httpx
import uvicorn
import time
import asyncio
from typing import List

from . import models, schemas, crud
from .database import SessionLocal, engine

# 데이터베이스 테이블 생성
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Service 2")

# Config 서비스 및 Discovery 서비스 URL
CONFIG_SERVICE_URL = "http://config:8888"
DISCOVERY_SERVICE_URL = "http://discovery:8761"
SERVICE_NAME = "service2"
SERVICE_URL = "http://service2:8082"

# 설정 정보
service_config = {}

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    # Config 서비스에서 설정 가져오기
    await fetch_config()
    
    # Discovery 서비스에 등록
    await register_service()
    
    # 주기적인 하트비트 전송 태스크 시작
    asyncio.create_task(send_heartbeat())

async def fetch_config():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{CONFIG_SERVICE_URL}/configs/{SERVICE_NAME}")
            if response.status_code == 200:
                global service_config
                service_config = response.json()
                print(f"Retrieved config: {service_config}")
        except Exception as e:
            print(f"Error fetching config: {e}")

async def register_service():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{DISCOVERY_SERVICE_URL}/register",
                json={"name": SERVICE_NAME, "url": SERVICE_URL}
            )
            if response.status_code == 200:
                print(f"Service registered successfully")
            else:
                print(f"Failed to register service: {response.text}")
        except Exception as e:
            print(f"Error registering service: {e}")

async def send_heartbeat():
    while True:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{DISCOVERY_SERVICE_URL}/heartbeat/{SERVICE_NAME}"
                )
                if response.status_code == 200:
                    print(f"Heartbeat sent successfully")
                else:
                    print(f"Failed to send heartbeat: {response.text}")
        except Exception as e:
            print(f"Error sending heartbeat: {e}")
        
        # 30초마다 하트비트 전송
        await asyncio.sleep(30)

@app.get("/")
async def root():
    return {"message": "Service 2 is running"}

@app.post("/orders/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    # Service1의 아이템 확인 (실제로는 API 호출)
    return crud.create_order(db=db, order=order)

@app.get("/orders/", response_model=List[schemas.Order])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    orders = crud.get_orders(db, skip=skip, limit=limit)
    return orders

@app.get("/orders/{order_id}", response_model=schemas.Order)
def read_order(order_id: int, db: Session = Depends(get_db)):
    db_order = crud.get_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@app.put("/orders/{order_id}", response_model=schemas.Order)
def update_order(order_id: int, order: schemas.OrderUpdate, db: Session = Depends(get_db)):
    db_order = crud.get_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return crud.update_order(db=db, order_id=order_id, order=order)

@app.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    db_order = crud.get_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    crud.delete_order(db=db, order_id=order_id)
    return {"message": "Order deleted successfully"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8082, reload=True)