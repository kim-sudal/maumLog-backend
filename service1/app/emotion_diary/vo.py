from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DiaryCreateRequest(BaseModel):
    user_idx: int
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
    page: int = 1
    page_size: int = 10

class DiaryDateRangeRequest(BaseModel):
    user_idx: int
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD

class DiaryVO(BaseModel):
    diary_idx: int
    user_idx: int
    content: str
    condition1: Optional[str] = None
    condition2: Optional[str] = None
    condition3: Optional[str] = None
    ai_select: Optional[str] = None  
    condition1_response: Optional[str] = None
    condition2_response: Optional[str] = None
    condition3_response: Optional[str] = None
    ai_response: Optional[str] = None
    ai_model: Optional[str] = None
    status_code: str
    reg_date: datetime
    update_date: Optional[datetime] = None
    record_date: Optional[datetime] = None