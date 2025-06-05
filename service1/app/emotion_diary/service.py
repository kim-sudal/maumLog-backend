from typing import Dict, Any, List, Optional
from ..common.common_vo import ChatGPTRequestVO
from ..common.common_service import ChatGPTService
from ..common.common_repository import ChatGPTRepository
from .vo import DiaryVO, DiaryCreateRequest, DiaryUpdateRequest
from .repository import EmotionDiaryRepository
from datetime import datetime
import traceback

class EmotionDiaryService:
    def __init__(self, repo: EmotionDiaryRepository):
        self.repo = repo
        # ChatGPT 서비스는 기존 방식 유지 (채팅용)
        self.chat_service = ChatGPTService(ChatGPTRepository(repo.db))
    
    def get_ai_response(self, vo: DiaryVO) -> DiaryVO:
        """기존 AI 응답 생성 메서드 (변경 없음)"""
        if not vo.content or not vo.content.strip():
            return DiaryVO(success=False, error="감정일기 내용이 비어있습니다.", status_code="400")
        
        try:
            # 조건들 수집
            conditions = [cond.strip() for cond in [vo.condition1, vo.condition2, vo.condition3, vo.condition4, vo.condition5, vo.condition6] if cond and cond.strip()]
            
            # ChatGPT 호출 (한 번의 호출로 모든 응답 받기)
            chat_request = ChatGPTRequestVO(prompt=vo.content, max_tokens=1500, temperature=0.7)
            chat_response = self.chat_service.get_chat_response(chat_request, conditions)
            
            # 에러 응답 처리
            if hasattr(chat_response, 'error'):
                return DiaryVO(success=False, error=chat_response.error, status_code=chat_response.status_code)
            
            # 기본 응답 설정
            result_vo = DiaryVO(
                success=True,
                ai_response=chat_response.content,
                model=chat_response.model
            )
            
            # 구조화된 응답이 있으면 각 필드에 매핑
            if hasattr(chat_response, 'structured_responses') and chat_response.structured_responses:
                structured = chat_response.structured_responses
                
                # 기본 응답
                if 'base_response' in structured:
                    result_vo.ai_response = structured['base_response']
                
                # 각 조건별 응답 매핑
                if 'condition1_response' in structured:
                    result_vo.condition1_response = structured['condition1_response']
                if 'condition2_response' in structured:
                    result_vo.condition2_response = structured['condition2_response']
                if 'condition3_response' in structured:
                    result_vo.condition3_response = structured['condition3_response']
                if 'condition4_response' in structured:
                    result_vo.condition4_response = structured['condition4_response']
                if 'condition5_response' in structured:
                    result_vo.condition5_response = structured['condition5_response'] 
                if 'condition6_response' in structured:
                    result_vo.condition6_response = structured['condition6_response']                                               
                
                # 원본 조건들도 다시 설정 (응답에 포함하기 위해)
                result_vo.condition1 = vo.condition1
                result_vo.condition2 = vo.condition2
                result_vo.condition3 = vo.condition3
                result_vo.condition4 = vo.condition4
                result_vo.condition5 = vo.condition5
                result_vo.condition6 = vo.condition6
            
            return result_vo
            
        except Exception as e:
            print(f"❌ 감정일기 처리 중 예외 발생: {str(e)}")
            traceback.print_exc()
            return DiaryVO(success=False, error=f"처리 중 오류가 발생했습니다: {str(e)}", status_code="500")
    
    # ===== 새로운 CRUD 메서드들 =====
    def create(self, vo: DiaryCreateRequest) -> int:
        """감정일기 생성"""
        return self.repo.create(vo)
    
    def get(self, diary_idx: int) -> Optional[dict]:
        """감정일기 조회"""
        return self.repo.get(diary_idx)
    
    def update(self, diary_idx: int, vo: DiaryUpdateRequest) -> bool:
        """감정일기 수정"""
        return self.repo.update(diary_idx, vo)
    
    def delete(self, diary_idx: int) -> bool:
        """감정일기 삭제"""
        return self.repo.delete(diary_idx)
    
    def get_list(self, user_idx: int = None, start_date: str = None, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """감정일기 목록 조회 (월별 필터링 포함)"""
        diaries, total_count = self.repo.get_list(user_idx, start_date, page, page_size)
        
        # 페이징 정보 계산
        total_pages = (total_count + page_size - 1) // page_size
        has_next = page < total_pages
        has_prev = page > 1
        
        return {
            'data': diaries,
            'pagination': {
                'current_page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_next': has_next,
                'has_prev': has_prev
            }
        }