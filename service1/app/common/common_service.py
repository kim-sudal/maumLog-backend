from typing import Union, List
from .common_vo import ChatGPTRequestVO, ChatGPTResponseVO, ChatGPTErrorVO, UsageInfo
from .common_repository import ChatGPTRepository
import traceback

class ChatGPTService:
    def __init__(self, repo: ChatGPTRepository):
        self.repo = repo
        
    def get_chat_response(self, vo: ChatGPTRequestVO, conditions: List[str] = None) -> Union[ChatGPTResponseVO, ChatGPTErrorVO]:
        """ChatGPT API로부터 구조화된 응답을 받아 처리하는 서비스 함수"""
        try:
            print(f"=== ChatGPTService.get_chat_response 호출 ===")
            if conditions:
                print(f"조건들: {conditions}")
                        
            # Repository에 조건들을 전달
            response_data = self.repo.send_prompt(vo, conditions)
                        
            # 에러 응답 처리
            if "error" in response_data:
                print(f"❌ Repository에서 에러 반환: {response_data['error']}")
                return ChatGPTErrorVO(
                    error=response_data["error"],
                    status_code=response_data["status_code"]
                )
                        
            # 성공 응답 처리
            try:
                content = response_data["choices"][0]["message"]["content"]
                model = response_data["model"]
                
                # usage 정보를 안전하게 처리
                usage_data = response_data.get("usage")
                usage = None
                if usage_data:
                    try:
                        usage = UsageInfo(**usage_data)
                        print(f"✅ usage 정보 파싱 성공")
                    except Exception as usage_error:
                        print(f"⚠️ usage 파싱 실패, 원본 데이터 사용: {usage_error}")
                        usage = usage_data
                
                # 구조화된 응답이 있는지 확인
                structured_responses = response_data.get("parsed_responses")
                
                response = ChatGPTResponseVO(
                    content=content,
                    model=model,
                    usage=usage,
                    structured_responses=structured_responses  # 구조화된 응답 추가
                )
                print(f"✅ ChatGPTResponseVO 생성 성공")
                return response
                            
            except (KeyError, IndexError) as e:
                error_msg = f"응답 파싱 오류: {str(e)}"
                print(f"❌ {error_msg}")
                print(f"응답 데이터 구조: {response_data}")
                return ChatGPTErrorVO(
                    error=error_msg,
                    status_code="500"
                )
                        
        except Exception as e:
            print(f"❌ ChatGPTService에서 예외 발생:")
            print(f"예외 타입: {type(e).__name__}")
            print(f"예외 메시지: {str(e)}")
            traceback.print_exc()
            return ChatGPTErrorVO(
                error=f"서비스 처리 중 오류: {str(e)}",
                status_code="500"
            )