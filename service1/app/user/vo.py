from pydantic import BaseModel
from typing import Optional


class UserVO(BaseModel):
    # 요청 시 필드 (회원가입, 로그인, 중복체크 등에 사용)
    login_id: Optional[str] = None
    login_password: Optional[str] = None
    password_confirm: Optional[str] = None  # 비밀번호 확인용 (회원가입 시)
    user_name: Optional[str] = None
    birth_date: Optional[str] = None  # YYYYMMDD 형식
    gender_code: Optional[str] = None  # M, F 등
    phone_number: Optional[str] = None
    email: Optional[str] = None
    user_description: Optional[str] = None
    
    # 응답 시 공통 필드
    success: Optional[bool] = None
    
    # 성공 시 필드
    user_idx: Optional[int] = None
    message: Optional[str] = None
    available: Optional[bool] = None  # 중복체크 시 사용가능 여부
    
    # 실패 시 필드
    error: Optional[str] = None
    status_code: Optional[int] = None

    access_token: Optional[str] = None 