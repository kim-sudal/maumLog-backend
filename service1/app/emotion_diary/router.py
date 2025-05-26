from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .vo import (
    DiaryVO, DiaryCreateRequest, DiaryUpdateRequest, DiaryDeleteRequest, 
    DiaryGetRequest, DiaryListRequest, DiaryDateRangeRequest
)
from .service import EmotionDiaryService
from .repository import EmotionDiaryRepository
from app.database import get_db
from datetime import datetime
from typing import Dict, Any
import traceback

router = APIRouter(prefix="/diaryChat", tags=["diary_chat"])

def get_service(db: Session = Depends(get_db)) -> EmotionDiaryService:
    repo = EmotionDiaryRepository(db)
    return EmotionDiaryService(repo)

# ===== 기존 AI 채팅 엔드포인트 (변경 없음) =====
@router.post("", response_model=DiaryVO)
def get_emotion_response(
    vo: DiaryVO, 
    service: EmotionDiaryService = Depends(get_service)
):
    """감정일기에 대한 AI 응답을 받는 엔드포인트"""
    try:
        print(f"=== /diaryChat 요청 받음 ===")
        print(f"요청 내용: {vo.content}")
        print(f"조건들: condition1={vo.condition1}, condition2={vo.condition2}, condition3={vo.condition3}, condition4={vo.condition4}")
        
        response = service.get_ai_response(vo)
        
        # 에러 응답인 경우 HTTPException 발생
        if not response.success:
            print(f"❌ 서비스 에러: {response.error}")
            raise HTTPException(
                status_code=response.status_code or 500,
                detail=response.error or "알 수 없는 오류가 발생했습니다."
            )
        
        print(f"✅ 성공 응답 반환")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 라우터에서 예외 발생: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"서버 내부 오류: {str(e)}"
        )

# ===== 새로운 CRUD 엔드포인트들 (모두 POST) =====
@router.post("/create", response_model=int)
def create_diary(
    vo: DiaryCreateRequest, 
    service: EmotionDiaryService = Depends(get_service)
):
    """감정일기 생성"""
    try:
        print(f"=== /diaryChat/create 요청 받음 ===")
        print(f"사용자: {vo.user_idx}, 내용: {vo.content[:50]}...")
        
        diary_idx = service.create(vo)
        if not diary_idx:
            raise HTTPException(status_code=500, detail="감정일기 생성에 실패했습니다.")
        
        print(f"✅ 감정일기 생성 성공: ID={diary_idx}")
        return diary_idx
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 감정일기 생성 중 예외 발생: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"감정일기 생성 중 오류: {str(e)}"
        )

@router.post("/get", response_model=dict)
def get_diary(
    vo: DiaryGetRequest,
    service: EmotionDiaryService = Depends(get_service)
):
    """단일 감정일기 조회"""
    try:
        print(f"=== /diaryChat/get 요청 받음 ===")
        print(f"일기 ID: {vo.diary_idx}")
        
        diary = service.get(vo.diary_idx)
        if not diary:
            raise HTTPException(status_code=404, detail="해당 일기를 찾을 수 없습니다.")
        
        print(f"✅ 감정일기 조회 성공: ID={vo.diary_idx}")
        return diary
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 감정일기 조회 중 예외 발생: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"감정일기 조회 중 오류: {str(e)}"
        )

@router.post("/update", response_model=bool)
def update_diary(
    vo: DiaryUpdateRequest,
    service: EmotionDiaryService = Depends(get_service)
):
    """감정일기 수정"""
    try:
        print(f"=== /diaryChat/update 요청 받음 ===")
        print(f"일기 ID: {vo.diary_idx}")
        
        success = service.update(vo.diary_idx, vo)
        if not success:
            raise HTTPException(status_code=404, detail="해당 일기를 찾을 수 없거나 수정에 실패했습니다.")
        
        print(f"✅ 감정일기 수정 성공: ID={vo.diary_idx}")
        return success
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 감정일기 수정 중 예외 발생: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"감정일기 수정 중 오류: {str(e)}"
        )

@router.post("/delete", response_model=bool)
def delete_diary(
    vo: DiaryDeleteRequest,
    service: EmotionDiaryService = Depends(get_service)
):
    """감정일기 삭제 (논리삭제)"""
    try:
        print(f"=== /diaryChat/delete 요청 받음 ===")
        print(f"일기 ID: {vo.diary_idx}")
        
        success = service.delete(vo.diary_idx)
        if not success:
            raise HTTPException(status_code=404, detail="해당 일기를 찾을 수 없거나 삭제에 실패했습니다.")
        
        print(f"✅ 감정일기 삭제 성공: ID={vo.diary_idx}")
        return success
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 감정일기 삭제 중 예외 발생: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"감정일기 삭제 중 오류: {str(e)}"
        )

@router.post("/list")
def get_diary_list(
    vo: DiaryListRequest,
    service: EmotionDiaryService = Depends(get_service)
) -> Dict[str, Any]:
    """감정일기 목록 조회 (페이징)"""
    try:
        print(f"=== /diaryChat/list 요청 받음 ===")
        print(f"사용자: {vo.user_idx}, 페이지: {vo.page}, 크기: {vo.page_size}")
        
        result = service.get_list(vo.user_idx, vo.page, vo.page_size)
        
        print(f"✅ 감정일기 목록 조회 성공: {len(result['data'])}개")
        return result
        
    except Exception as e:
        print(f"❌ 감정일기 목록 조회 중 예외 발생: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"감정일기 목록 조회 중 오류: {str(e)}"
        )

@router.post("/date-range")
def get_diaries_by_date_range(
    vo: DiaryDateRangeRequest,
    service: EmotionDiaryService = Depends(get_service)
) -> Dict[str, Any]:
    """날짜 범위로 감정일기 조회"""
    try:
        print(f"=== /diaryChat/date-range 요청 받음 ===")
        print(f"사용자: {vo.user_idx}, 기간: {vo.start_date} ~ {vo.end_date}")
        
        # 날짜 문자열을 datetime 객체로 변환
        try:
            start_dt = datetime.strptime(vo.start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(vo.end_date, "%Y-%m-%d")
            # 종료일은 해당 날짜의 마지막 시간으로 설정
            end_dt = end_dt.replace(hour=23, minute=59, second=59)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식을 사용해주세요."
            )
        
        if start_dt > end_dt:
            raise HTTPException(
                status_code=400,
                detail="시작일이 종료일보다 늦을 수 없습니다."
            )
        
        diaries = service.get_by_date_range(vo.user_idx, start_dt, end_dt)
        
        result = {
            'data': diaries,
            'count': len(diaries),
            'date_range': {
                'start_date': vo.start_date,
                'end_date': vo.end_date
            }
        }
        
        print(f"✅ 날짜별 감정일기 조회 성공: {len(diaries)}개")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 날짜별 감정일기 조회 중 예외 발생: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"날짜별 감정일기 조회 중 오류: {str(e)}"
        )

# 헬스 체크용 엔드포인트
@router.get("/health")
def health_check():
    """감정일기 API 상태 확인"""
    return {
        "status": "healthy",
        "service": "emotion_diary",
        "timestamp": datetime.now().isoformat()
    }