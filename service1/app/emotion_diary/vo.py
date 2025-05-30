from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DiaryCreateRequest(BaseModel):
    content: str
    condition1: Optional[str] = None
    condition2: Optional[str] = None
    condition3: Optional[str] = None
    condition4: Optional[str] = None
    condition1_response: Optional[str] = None
    condition2_response: Optional[str] = None
    condition3_response: Optional[str] = None
    condition4_response: Optional[str] = None 
    ai_response: Optional[str] = None
    ai_model: Optional[str] = None
    record_date: Optional[datetime] = None    
    user_idx: Optional[int] = None

class DiaryUpdateRequest(BaseModel):
    diary_idx: int
    content: Optional[str] = None
    condition1: Optional[str] = None
    condition2: Optional[str] = None
    condition3: Optional[str] = None
    condition4: Optional[str] = None
    condition1_response: Optional[str] = None
    condition2_response: Optional[str] = None
    condition3_response: Optional[str] = None
    condition4_response: Optional[str] = None  
    ai_response: Optional[str] = None
    ai_model: Optional[str] = None
    record_date: Optional[datetime] = None

class DiaryDeleteRequest(BaseModel):
    diary_idx: int

class DiaryGetRequest(BaseModel):
    diary_idx: int

class DiaryListRequest(BaseModel):
    user_idx: Optional[int] = None
    start_date: Optional[str] = None  # "2024-05" 형식 추가
    page: int = 1
    page_size: int = 10

class DiaryListRequest(BaseModel):
    page: int = 1
    page_size: int = 10
    start_date: Optional[str] = None  # "2025-05" 형식

class DiaryVO(BaseModel):
    diary_idx: Optional[int] = None
    user_idx: Optional[int] = None
    content: Optional[str] = None
    condition1: Optional[str] = None
    condition2: Optional[str] = None
    condition3: Optional[str] = None
    condition4: Optional[str] = None
    ai_select: Optional[str] = None      
    condition1_response: Optional[str] = None
    condition2_response: Optional[str] = None
    condition3_response: Optional[str] = None
    condition4_response: Optional[str] = None  
    ai_response: Optional[str] = None
    ai_model: Optional[str] = None
    status_code: Optional[str] = None
    reg_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    record_date: Optional[datetime] = None
    success: Optional[bool] = None 
    error: Optional[str] = None