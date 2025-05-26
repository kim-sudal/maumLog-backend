import os
from fastapi import FastAPI, HTTPException, Request
from typing import Dict, Any

app = FastAPI(title="Config Service")

config_store: Dict[str, Dict[str, Any]] = {
    "service1": {
        "timeout": 60,
        "cors_origins": ["http://localhost:3000"]
    },
    "service2": {
        "timeout": 60,
        "cors_origins": ["http://localhost:3000"]
    },
    "gateway": {
        "timeout": 60,
        "cors_origins": ["http://localhost:3000"]
    }
}

@app.get("/")
async def root():
    return {"message": "Config Service is running"}

@app.get("/configs/{service_name}")
async def get_config(service_name: str):
    if service_name not in config_store:
        raise HTTPException(status_code=404, detail=f"Config for {service_name} not found")
    return config_store[service_name]

@app.put("/configs/{service_name}")
async def update_config(service_name: str, request: Request):
    new_config = await request.json()
    config_store[service_name] = new_config
    return {"message": f"Config for {service_name} updated successfully"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
