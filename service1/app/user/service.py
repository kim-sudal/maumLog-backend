from typing import Union
from .vo import UserVO
from .repository import UserRepository
import traceback
import re


class UserService:
    def __init__(self, db):
        self.db = db
        self.repository = UserRepository(db)
    
    def signup_user(self, vo: UserVO) -> UserVO:
        """회원가입 처리"""
        try:
            # 필수 필드 검증
            validation_result = self._validate_signup_fields(vo)
            if not validation_result.success:
                return validation_result
            
            # 로그인 ID 중복 체크
            if self.repository.check_login_id_exists(vo.login_id):
                return UserVO(success=False, error="이미 사용중인 로그인 아이디입니다.", status_code=400)
            
            # 이메일 중복 체크 (이메일이 있는 경우)
            if vo.email and self.repository.check_email_exists(vo.email):
                return UserVO(success=False, error="이미 사용중인 이메일입니다.", status_code=400)
            
            # 사용자 생성
            user_data = {
                'login_id': vo.login_id,
                'login_password': vo.login_password,
                'user_name': vo.user_name,
                'birth_date': vo.birth_date,
                'gender_code': vo.gender_code,
                'phone_number': vo.phone_number,
                'email': vo.email,
                'user_description': vo.user_description
            }
            
            user_idx = self.repository.create_user(user_data)
            if user_idx:
                return UserVO(success=True, user_idx=user_idx, message="회원가입이 완료되었습니다.")
            else:
                return UserVO(success=False, error="회원가입 처리 중 오류가 발생했습니다.", status_code=500)
                
        except Exception as e:
            print(f"❌ 회원가입 서비스 오류: {str(e)}")
            traceback.print_exc()
            return UserVO(success=False, error="서버 오류가 발생했습니다.", status_code=500)
    
    def login_user(self, vo: UserVO) -> UserVO:
        """로그인 처리"""
        try:
            # 필수 필드 검증
            if not vo.login_id or not vo.login_id.strip():
                return UserVO(success=False, error="로그인 아이디를 입력해주세요.", status_code=400)
            
            if not vo.login_password or not vo.login_password.strip():
                return UserVO(success=False, error="비밀번호를 입력해주세요.", status_code=400)
            
            # 사용자 인증
            auth_result = self.repository.authenticate_user(vo.login_id, vo.login_password)
            
            if auth_result is None:
                return UserVO(success=False, error="로그인 아이디 또는 비밀번호가 일치하지 않습니다.", status_code=401)
            
            if auth_result.get('blocked'):
                return UserVO(success=False, error="차단된 계정입니다. 관리자에게 문의하세요.", status_code=403)
            
            return UserVO(
                success=True, 
                user_idx=auth_result['user_idx'],
                user_name=auth_result['user_name'],
                message="로그인이 완료되었습니다."
            )
            
        except Exception as e:
            print(f"❌ 로그인 서비스 오류: {str(e)}")
            traceback.print_exc()
            return UserVO(success=False, error="서버 오류가 발생했습니다.", status_code=500)
    
    def check_duplicate(self, vo: UserVO) -> UserVO:
        """중복 체크 (로그인 ID 또는 이메일)"""
        try:
            if vo.login_id:
                # 로그인 ID 중복 체크
                exists = self.repository.check_login_id_exists(vo.login_id)
                return UserVO(
                    success=True,
                    available=not exists,
                    message="사용 가능한 아이디입니다." if not exists else "이미 사용중인 아이디입니다."
                )
            
            elif vo.email:
                # 이메일 중복 체크
                exists = self.repository.check_email_exists(vo.email)
                return UserVO(
                    success=True,
                    available=not exists,
                    message="사용 가능한 이메일입니다." if not exists else "이미 사용중인 이메일입니다."
                )
            
            else:
                return UserVO(success=False, error="확인할 정보를 입력해주세요.", status_code=400)
                
        except Exception as e:
            print(f"❌ 중복체크 서비스 오류: {str(e)}")
            traceback.print_exc()
            return UserVO(success=False, error="서버 오류가 발생했습니다.", status_code=500)
    
    def _validate_signup_fields(self, vo: UserVO) -> UserVO:
        """회원가입 필드 검증"""
        # 필수 필드 체크
        if not vo.login_id or not vo.login_id.strip():
            return UserVO(success=False, error="로그인 아이디를 입력해주세요.", status_code=400)
        
        if not vo.login_password or not vo.login_password.strip():
            return UserVO(success=False, error="비밀번호를 입력해주세요.", status_code=400)
        
        if not vo.password_confirm or vo.login_password != vo.password_confirm:
            return UserVO(success=False, error="비밀번호가 일치하지 않습니다.", status_code=400)
        
        if not vo.user_name or not vo.user_name.strip():
            return UserVO(success=False, error="사용자 이름을 입력해주세요.", status_code=400)
        
        # 형식 검증
        # 로그인 ID 검증
        if len(vo.login_id) < 4 or len(vo.login_id) > 30:
            return UserVO(success=False, error="로그인 아이디는 4자 이상 30자 이하로 입력해주세요.", status_code=400)
        
        if not re.match(r'^[a-zA-Z0-9_]+$', vo.login_id):
            return UserVO(success=False, error="로그인 아이디는 영문, 숫자, 언더바(_)만 사용 가능합니다.", status_code=400)
        
        # 비밀번호 검증
        if len(vo.login_password) < 8:
            return UserVO(success=False, error="비밀번호는 8자 이상으로 설정해주세요.", status_code=400)
        
        if not re.search(r'[A-Za-z]', vo.login_password):
            return UserVO(success=False, error="비밀번호에는 영문자가 포함되어야 합니다.", status_code=400)
        
        if not re.search(r'\d', vo.login_password):
            return UserVO(success=False, error="비밀번호에는 숫자가 포함되어야 합니다.", status_code=400)
        
        # 생년월일 검증 
        if vo.birth_date and not re.match(r'^\d{8}$', vo.birth_date):
            return UserVO(success=False, error="생년월일은 YYYYMMDD 형식으로 입력해주세요.", status_code=400)
        
        # 성별 검증 
        if vo.gender_code and vo.gender_code not in ['M', 'F']:
            return UserVO(success=False, error="성별 코드는 M(남성) 또는 F(여성)만 입력 가능합니다.", status_code=400)
        
        # 전화번호 검증 
        if vo.phone_number and not re.match(r'^01[0-9]-\d{3,4}-\d{4}$', vo.phone_number):
            return UserVO(success=False, error="전화번호는 010-1234-5678 형식으로 입력해주세요.", status_code=400)
        
        # 이메일 검증 
        if vo.email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', vo.email):
            return UserVO(success=False, error="올바른 이메일 형식으로 입력해주세요.", status_code=400)
        
        return UserVO(success=True)