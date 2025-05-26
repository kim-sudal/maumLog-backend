from pydantic import BaseModel
from typing import Optional, Dict, Any

# OpenAI API usage 구조에 맞는 새로운 모델들
class TokenDetails(BaseModel):
    cached_tokens: Optional[int] = 0
    audio_tokens: Optional[int] = 0

class CompletionTokenDetails(BaseModel):
    reasoning_tokens: Optional[int] = 0
    accepted_prediction_tokens: Optional[int] = 0
    rejected_prediction_tokens: Optional[int] = 0

class UsageInfo(BaseModel):
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None       
    total_tokens: Optional[int] = None
    prompt_tokens_details: Optional[TokenDetails] = None
    completion_tokens_details: Optional[CompletionTokenDetails] = None

class ChatGPTRequestVO(BaseModel):
    prompt: str
    max_tokens: int = 1000
    temperature: float = 0.7
     
class ChatGPTResponseVO(BaseModel):
    content: str
    model: str
    usage: Optional[UsageInfo] = None  # 구체적인 usage 구조 정의
    structured_responses: Optional[Dict[str, str]] = None  # 구조화된 응답 추가
     
class ChatGPTErrorVO(BaseModel):
    error: str
    status_code: int