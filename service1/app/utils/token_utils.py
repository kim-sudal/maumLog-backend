# utils/token_utils.py (간단 버전)
import jwt
import os
from datetime import datetime, timedelta
from fastapi import Request, HTTPException

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"

class TokenUtils:
    @staticmethod
    def create_access_token(user_idx: str, login_id: str, user_name: str) -> str:
        payload = {
            "user_idx": user_idx,
            "login_id": login_id,
            "user_name": user_name,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def get_user_idx_from_token(token: str) -> str:
        if token.startswith("Bearer "):
            token = token[7:]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("user_idx")

def get_current_user_idx(request: Request) -> str:
    auth_header = request.headers.get("authorization")
    if not auth_header:
        return None
    try:
        return TokenUtils.get_user_idx_from_token(auth_header)
    except:
        return None