from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .vo import UserVO
from .service import UserService
from app.database import get_db  # 올바른 import 경로
import traceback

router = APIRouter(prefix="/user", tags=["user"])

def get_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

@router.post("/signup", response_model=UserVO)
def signup_user(
    vo: UserVO, 
    service: UserService = Depends(get_service)
):
    """회원가입 엔드포인트"""
    try:
        print(f"=== /user/signup 요청 받음 ===")
        print(f"로그인 ID: {vo.login_id}")
        print(f"사용자 이름: {vo.user_name}")
        print(f"이메일: {vo.email}")
        
        response = service.signup_user(vo)
        
        # 에러 응답인 경우 HTTPException 발생
        if not response.success:
            print(f"❌ 회원가입 실패: {response.error}")
            raise HTTPException(
                status_code=response.status_code or 500,
                detail=response.error or "알 수 없는 오류가 발생했습니다."
            )
        
        print(f"✅ 회원가입 성공: USER_IDX={response.user_idx}")
        # 응답에서 비밀번호 정보 제거
        response.login_password = None
        response.password_confirm = None
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
    """로그인 엔드포인트"""
    try:
        print(f"=== /user/login 요청 받음 ===")
        print(f"로그인 ID: {vo.login_id}")
        
        response = service.login_user(vo)
        
        # 에러 응답인 경우 HTTPException 발생
        if not response.success:
            print(f"❌ 로그인 실패: {response.error}")
            raise HTTPException(
                status_code=response.status_code or 500,
                detail=response.error or "알 수 없는 오류가 발생했습니다."
            )
        
        print(f"✅ 로그인 성공: USER_IDX={response.user_idx}, USER_NAME={response.user_name}")
        # 응답에서 비밀번호 정보 제거
        response.login_password = None
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
    """중복체크 엔드포인트 (로그인 ID 또는 이메일)"""
    try:
        print(f"=== /user/check 요청 받음 ===")
        print(f"체크할 로그인 ID: {vo.login_id}")
        print(f"체크할 이메일: {vo.email}")
        
        response = service.check_duplicate(vo)
        
        # 에러 응답인 경우 HTTPException 발생
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