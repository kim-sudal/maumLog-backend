from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from .vo import UserVO
from .service import UserService
from app.database import get_db
from app.utils.token_utils import TokenUtils, get_current_user_idx  # 토큰 유틸만 추가
import traceback

router = APIRouter(prefix="/user", tags=["user"])

def get_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

@router.post("/signup", response_model=UserVO)
def signup_user(
    vo: UserVO, 
    service: UserService = Depends(get_service)
):
    """회원가입 엔드포인트 (기존 그대로)"""
    try:
        print(f"=== /user/signup 요청 받음 ===")
        print(f"로그인 ID: {vo.login_id}")
        print(f"사용자 이름: {vo.user_name}")
        print(f"이메일: {vo.email}")
        
        response = service.signup_user(vo)
        
        if not response.success:
            print(f"❌ 회원가입 실패: {response.error}")
            raise HTTPException(
                status_code=response.status_code or 500,
                detail=response.error or "알 수 없는 오류가 발생했습니다."
            )
        
        print(f"✅ 회원가입 성공: USER_IDX={response.user_idx}")
        response.login_password = None
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 회원가입 라우터에서 예외 발생: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"서버 내부 오류: {str(e)}"
        )

@router.post("/login", response_model=UserVO)
def login_user(
    vo: UserVO, 
    service: UserService = Depends(get_service)
):
    """로그인 엔드포인트 (토큰 발급 추가)"""
    try:
        print(f"=== /user/login 요청 받음 ===")
        print(f"로그인 ID: {vo.login_id}")
        
        response = service.login_user(vo)
        
        if not response.success:
            print(f"❌ 로그인 실패: {response.error}")
            raise HTTPException(
                status_code=response.status_code or 401,
                detail=response.error or "로그인에 실패했습니다."
            )
        
        print(f"✅ 로그인 성공: USER_IDX={response.user_idx}, USER_NAME={response.user_name}")
        
        # 토큰 생성해서 응답에 추가 (기존 response 객체에 token 필드만 추가)
        token = TokenUtils.create_access_token(
            user_idx=response.user_idx,
            login_id=vo.login_id,
            user_name=response.user_name
        )
        
        # 기존 응답에 토큰만 추가
        response.access_token = token  # UserVO에 access_token 필드 추가 필요
        response.login_password = None
        
        print(f"✅ 토큰 발급 완료")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 로그인 라우터에서 예외 발생: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"서버 내부 오류: {str(e)}"
        )

@router.post("/check", response_model=UserVO)
def check_duplicate(
    vo: UserVO, 
    service: UserService = Depends(get_service)
):
    """중복체크 엔드포인트 (기존 그대로)"""
    try:
        print(f"=== /user/check 요청 받음 ===")
        print(f"체크할 로그인 ID: {vo.login_id}")
        print(f"체크할 이메일: {vo.email}")
        
        response = service.check_duplicate(vo)
        
        if not response.success:
            print(f"❌ 중복체크 실패: {response.error}")
            raise HTTPException(
                status_code=response.status_code or 500,
                detail=response.error or "알 수 없는 오류가 발생했습니다."
            )
        
        print(f"✅ 중복체크 완료: available={response.available}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 중복체크 라우터에서 예외 발생: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"서버 내부 오류: {str(e)}"
        )
    
@router.post("/profile", response_model=UserVO)
def get_user_profile(
    current_user_idx: int = Depends(get_current_user_idx),
    service: UserService = Depends(get_service)
):
    """유저 개인정보 조회 엔드포인트"""
    try:
        print(f"=== /user/profile 요청 받음 ===")
        print(f"조회 대상 USER_IDX: {current_user_idx}")
        
        response = service.get_user_profile(current_user_idx)
        
        if not response.success:
            print(f"❌ 개인정보 조회 실패: {response.error}")
            raise HTTPException(
                status_code=response.status_code or 500,
                detail=response.error or "개인정보 조회 중 오류가 발생했습니다."
            )
        
        print(f"✅ 개인정보 조회 성공: USER_IDX={response.user_idx}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 개인정보 조회 라우터에서 예외 발생: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"서버 내부 오류: {str(e)}"
        )

@router.post("/profile/update", response_model=UserVO)
def update_user_profile(
    vo: UserVO,
    current_user_idx: int = Depends(get_current_user_idx),
    service: UserService = Depends(get_service)
):
    """유저 개인정보 수정 엔드포인트"""
    try:
        print(f"=== /user/profile/update 요청 받음 ===")
        print(f"수정 대상 USER_IDX: {current_user_idx}")
        print(f"수정 내용: {vo}")
        
        response = service.update_user_profile(current_user_idx, vo)
        
        if not response.success:
            print(f"❌ 개인정보 수정 실패: {response.error}")
            raise HTTPException(
                status_code=response.status_code or 500,
                detail=response.error or "개인정보 수정 중 오류가 발생했습니다."
            )
        
        print(f"✅ 개인정보 수정 성공: USER_IDX={response.user_idx}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 개인정보 수정 라우터에서 예외 발생: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"서버 내부 오류: {str(e)}"
        )    