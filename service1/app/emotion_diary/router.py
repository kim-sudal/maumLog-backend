from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.token_utils import get_current_user_idx  # 토큰에서 user_idx 추출
from .vo import DiaryVO, DiaryCreateRequest, DiaryUpdateRequest, DiaryGetRequest ,DiaryListRequest
from .service import EmotionDiaryService
from .repository import EmotionDiaryRepository
from datetime import datetime
from typing import Optional
import traceback

router = APIRouter(prefix="/diaryChat", tags=["emotion_diary"])

def get_service(db: Session = Depends(get_db)) -> EmotionDiaryService:
    repo = EmotionDiaryRepository(db)
    return EmotionDiaryService(repo)

@router.post("/ai-response", response_model=DiaryVO)
def get_ai_response(
    vo: DiaryVO,
    service: EmotionDiaryService = Depends(get_service)
):
    """AI 응답 생성 (기존 그대로)"""
    try:
        print(f"=== /diary/ai-response 요청 받음 ===")
        print(f"Content: {vo.content[:100]}..." if vo.content and len(vo.content) > 100 else f"Content: {vo.content}")
        
        response = service.get_ai_response(vo)
        
        if not response.success:
            print(f"❌ AI 응답 생성 실패: {response.error}")
            raise HTTPException(
                status_code=int(response.status_code) if response.status_code else 500,
                detail=response.error
            )
        
        print(f"✅ AI 응답 생성 성공")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ AI 응답 라우터에서 예외 발생: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"서버 내부 오류: {str(e)}"
        )

# 기존 스타일 그대로 유지, 토큰에서 user_idx만 추출해서 사용
@router.post("/create")
def create_diary(
    vo: DiaryCreateRequest,
    request: Request,  # 토큰 추출용
    service: EmotionDiaryService = Depends(get_service)
):
    """감정일기 생성 (토큰에서 user_idx 추출)"""
    try:
        print(f"=== /diary/create 요청 받음 ===")
        
        # 토큰에서 user_idx 추출
        user_idx = get_current_user_idx(request)
        if not user_idx:
            raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
        
        print(f"User IDX (from token): {user_idx}")
        print(f"Content: {vo.content[:100]}..." if vo.content and len(vo.content) > 100 else f"Content: {vo.content}")
        
        # VO에 user_idx 설정 (기존 방식 그대로)
        vo.user_idx = user_idx
        
        # 기존 서비스 호출 방식 그대로
        diary_idx = service.create(vo)
        
        return {
            "success": True,
            "message": "감정일기가 성공적으로 생성되었습니다.",
            "diary_idx": diary_idx,
            "user_idx": user_idx
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 감정일기 생성 라우터에서 예외 발생: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"서버 내부 오류: {str(e)}"
        )

@router.post("/list")
def get_diary_list(
    request_data: DiaryListRequest,  # ← Request Body로 받기
    request: Request,  # 토큰 추출용
    service: EmotionDiaryService = Depends(get_service)
):
    """감정일기 목록 조회 (토큰에서 user_idx 추출)"""
    try:
        print(f"=== /diary/list 요청 받음 ===")
        
        # 토큰에서 user_idx 추출
        user_idx = get_current_user_idx(request)
        if not user_idx:
            raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
        
        print(f"User IDX (from token): {user_idx}")
        print(f"Start Date: {request_data.start_date}")      
        print(f"Page: {request_data.page}, Page Size: {request_data.page_size}")  
        
        # 서비스 호출
        result = service.get_list(user_idx, request_data.start_date, request_data.page, request_data.page_size)
        
        return {
            "success": True,
            "message": "감정일기 목록 조회 성공",
            "data": result['data'],
            "pagination": result['pagination']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 감정일기 목록 조회 라우터에서 예외 발생: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"서버 내부 오류: {str(e)}"
        )

@router.post("/detail")
def get_diary_detail(
    request_data: DiaryGetRequest,  # 이 부분만 변경 (기존: diary_idx: int)
    request: Request,  # 토큰 추출용
    service: EmotionDiaryService = Depends(get_service)
):
    """감정일기 상세 조회 (토큰에서 user_idx 추출해서 권한 체크)"""
    try:
        print(f"=== /diary/detail 요청 받음 ===")
        
        # 토큰에서 user_idx 추출
        user_idx = get_current_user_idx(request)
        if not user_idx:
            raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
        
        diary_idx = request_data.diary_idx  # 이 부분만 변경
        print(f"User IDX (from token): {user_idx}")
        print(f"Diary IDX: {diary_idx}")
        
        # 기존 서비스 호출
        diary = service.get(diary_idx)
        
        # 권한 체크 (본인 것만 조회 가능)
        if not diary or diary.get('user_idx') != user_idx:
            raise HTTPException(
                status_code=404,
                detail="감정일기를 찾을 수 없거나 접근 권한이 없습니다."
            )
        
        return {
            "success": True,
            "message": "감정일기 조회 성공",
            "data": diary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 감정일기 조회 라우터에서 예외 발생: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"서버 내부 오류: {str(e)}"
        )

@router.post("/update")
def update_diary(
    request_data: DiaryUpdateRequest,  # 이 부분도 동일하게 변경
    request: Request,  # 토큰 추출용
    service: EmotionDiaryService = Depends(get_service)
):
    """감정일기 수정 (토큰에서 user_idx 추출해서 권한 체크)"""
    try:
        print(f"=== /diary/update 요청 받음 ===")
        
        # 토큰에서 user_idx 추출
        user_idx = get_current_user_idx(request)
        if not user_idx:
            raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
        
        diary_idx = request_data.diary_idx  # 이 부분 변경
        print(f"User IDX (from token): {user_idx}")
        print(f"Diary IDX: {diary_idx}")
        
        # 먼저 해당 일기가 본인 것인지 확인
        existing_diary = service.get(diary_idx)
        if not existing_diary or existing_diary.get('user_idx') != user_idx:
            raise HTTPException(
                status_code=404,
                detail="감정일기를 찾을 수 없거나 수정 권한이 없습니다."
            )
        
        # 기존 서비스 호출
        success = service.update(diary_idx, request_data)  # 이 부분도 변경
        
        if not success:
            raise HTTPException(status_code=500, detail="감정일기 수정에 실패했습니다.")
        
        return {
            "success": True,
            "message": "감정일기가 성공적으로 수정되었습니다.",
            "diary_idx": diary_idx,
            "user_idx": user_idx
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 감정일기 수정 라우터에서 예외 발생: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"서버 내부 오류: {str(e)}"
        )

@router.post("/delete")
def delete_diary(
    request_data: DiaryGetRequest,  # DELETE도 diary_idx만 필요하니까 DiaryGetRequest 재사용
    request: Request,  # 토큰 추출용
    service: EmotionDiaryService = Depends(get_service)
):
    """감정일기 삭제 (토큰에서 user_idx 추출해서 권한 체크)"""
    try:
        print(f"=== /diary/delete 요청 받음 ===")
        
        # 토큰에서 user_idx 추출
        user_idx = get_current_user_idx(request)
        if not user_idx:
            raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
        
        diary_idx = request_data.diary_idx  # 이 부분 변경
        print(f"User IDX (from token): {user_idx}")
        print(f"Diary IDX: {diary_idx}")
        
        # 먼저 해당 일기가 본인 것인지 확인
        existing_diary = service.get(diary_idx)
        if not existing_diary or existing_diary.get('user_idx') != user_idx:
            raise HTTPException(
                status_code=404,
                detail="감정일기를 찾을 수 없거나 삭제 권한이 없습니다."
            )
        
        # 기존 서비스 호출
        success = service.delete(diary_idx)
        
        if not success:
            raise HTTPException(status_code=500, detail="감정일기 삭제에 실패했습니다.")
        
        return {
            "success": True,
            "message": "감정일기가 성공적으로 삭제되었습니다.",
            "diary_idx": diary_idx,
            "user_idx": user_idx
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 감정일기 삭제 라우터에서 예외 발생: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"서버 내부 오류: {str(e)}"
        )