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
                'nickname': vo.nickname,
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

    def get_user_profile(self, user_idx: int) -> UserVO:
        """사용자 개인정보 조회"""
        try:
            print(f"=== 개인정보 조회 서비스 시작 ===")
            print(f"조회 대상 USER_IDX: {user_idx}")
            
            user_data = self.repository.get_user_by_idx(user_idx)
            
            if not user_data:
                print(f"❌ 사용자 정보를 찾을 수 없음: USER_IDX={user_idx}")
                return UserVO(success=False, error="사용자 정보를 찾을 수 없습니다.", status_code=404)
            
            print(f"✅ 개인정보 조회 완료: {user_data['login_id']}")
            
            return UserVO(
                success=True,
                user_idx=user_data['user_idx'],
                login_id=user_data['login_id'],
                user_name=user_data['user_name'],
                birth_date=user_data['birth_date'],
                nickname=user_data['nickname'],
                email=user_data['email'],
                user_description=user_data['user_description'],
                mbti=user_data['mbti'],
                message="개인정보 조회가 완료되었습니다."
            )
            
        except Exception as e:
            print(f"❌ 개인정보 조회 서비스 오류: {str(e)}")
            traceback.print_exc()
            return UserVO(success=False, error="서버 오류가 발생했습니다.", status_code=500)

    def update_user_profile(self, user_idx: int, vo: UserVO) -> UserVO:
        """사용자 개인정보 수정"""
        try:
            print(f"=== 개인정보 수정 서비스 시작 ===")
            print(f"수정 대상 USER_IDX: {user_idx}")
            
            # 사용자 존재 확인
            existing_user = self.repository.get_user_by_idx(user_idx)
            if not existing_user:
                print(f"❌ 사용자 정보를 찾을 수 없음: USER_IDX={user_idx}")
                return UserVO(success=False, error="사용자 정보를 찾을 수 없습니다.", status_code=404)
            
            # 수정할 데이터 준비
            update_data = {}
            
            if vo.user_name is not None:
                update_data['user_name'] = vo.user_name
                print(f"수정 요청 - 사용자명: {vo.user_name}")
            
            if vo.birth_date is not None:
                update_data['birth_date'] = vo.birth_date
                print(f"수정 요청 - 생년월일: {vo.birth_date}")
            
            if vo.nickname is not None:
                update_data['nickname'] = vo.nickname
                print(f"수정 요청 - 닉네임: {vo.nickname}")
            
            if vo.email is not None:
                # 이메일 중복 체크 (본인 제외)
                if self.repository.check_email_exists_exclude_user(vo.email, user_idx):
                    print(f"❌ 이메일 중복: {vo.email}")
                    return UserVO(success=False, error="이미 사용중인 이메일입니다.", status_code=400)
                update_data['email'] = vo.email
                print(f"수정 요청 - 이메일: {vo.email}")
            
            if vo.user_description is not None:
                update_data['user_description'] = vo.user_description
                print(f"수정 요청 - 사용자 설명: {vo.user_description}")
            
            if vo.mbti is not None:
                update_data['mbti'] = vo.mbti
                print(f"수정 요청 - MBTI: {vo.mbti}")
            
            if not update_data:
                print("❌ 수정할 정보가 없음")
                return UserVO(success=False, error="수정할 정보를 입력해주세요.", status_code=400)
            
            # 개인정보 수정
            update_success = self.repository.update_user(user_idx, update_data)
            
            if not update_success:
                print("❌ 개인정보 수정 실패")
                return UserVO(success=False, error="개인정보 수정에 실패했습니다.", status_code=500)
            
            print("✅ 개인정보 수정 성공")
            
            # 수정된 정보 다시 조회해서 반환
            return self.get_user_profile(user_idx)
            
        except Exception as e:
            print(f"❌ 개인정보 수정 서비스 오류: {str(e)}")
            traceback.print_exc()
            return UserVO(success=False, error="서버 오류가 발생했습니다.", status_code=500)    