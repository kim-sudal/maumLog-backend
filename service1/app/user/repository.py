from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, Dict, Any
import hashlib
import traceback


class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def check_login_id_exists(self, login_id: str) -> bool:
        """로그인 아이디 중복 체크"""
        try:
            query = text("""
                SELECT COUNT(*) as count 
                FROM tbl_user_info 
                WHERE LOGIN_ID = :login_id 
                AND STATUS_CODE = 'Y'
            """)
            result = self.db.execute(query, {"login_id": login_id}).fetchone()
            return result.count > 0
        except Exception as e:
            print(f"❌ 로그인 아이디 중복 체크 중 오류: {str(e)}")
            traceback.print_exc()
            return True  # 오류 시 중복으로 간주
    
    def check_email_exists(self, email: str) -> bool:
        """이메일 중복 체크"""
        try:
            query = text("""
                SELECT COUNT(*) as count 
                FROM tbl_user_info 
                WHERE EMAIL = :email 
                AND STATUS_CODE = 'Y'
            """)
            result = self.db.execute(query, {"email": email}).fetchone()
            return result.count > 0
        except Exception as e:
            print(f"❌ 이메일 중복 체크 중 오류: {str(e)}")
            traceback.print_exc()
            return True  # 오류 시 중복으로 간주

    def check_email_exists_exclude_user(self, email: str, user_idx: int) -> bool:
        """이메일 중복 체크 (특정 사용자 제외)"""
        try:
            query = text("""
                SELECT COUNT(*) as count 
                FROM tbl_user_info 
                WHERE EMAIL = :email 
                AND USER_IDX != :user_idx
                AND STATUS_CODE = 'Y'
            """)
            result = self.db.execute(query, {"email": email, "user_idx": user_idx}).fetchone()
            return result.count > 0
        except Exception as e:
            print(f"❌ 이메일 중복 체크(사용자 제외) 중 오류: {str(e)}")
            traceback.print_exc()
            return True  # 오류 시 중복으로 간주
    
    def create_user(self, user_data: Dict[str, Any]) -> Optional[int]:
        """사용자 생성"""
        try:
            # 비밀번호 해싱
            hashed_password = self._hash_password(user_data['login_password'])
            
            query = text("""
                INSERT INTO tbl_user_info (
                    LOGIN_ID, LOGIN_PASSWORD, USER_NAME, BIRTH_DATE, 
                    NICKNAME, EMAIL, USER_DESCRIPTION, MBTI,
                    STATUS_CODE, REG_DATE
                ) VALUES (
                    :login_id, :login_password, :user_name, :birth_date,
                    :nickname, :email, :user_description, :mbti,
                    'Y', NOW()
                )
            """)
            
            result = self.db.execute(query, {
                "login_id": user_data['login_id'],
                "login_password": hashed_password,
                "user_name": user_data['user_name'],
                "birth_date": user_data.get('birth_date'),
                "nickname": user_data.get('nickname'),
                "email": user_data.get('email'),
                "user_description": user_data.get('user_description'),
                "mbti": user_data.get('mbti'),
            })
            
            self.db.commit()
            
            # 생성된 사용자 ID 반환
            user_idx = result.lastrowid
            print(f"✅ 사용자 생성 완료: USER_IDX={user_idx}")
            return user_idx
            
        except Exception as e:
            print(f"❌ 사용자 생성 중 오류: {str(e)}")
            traceback.print_exc()
            self.db.rollback()
            return None
    
    def authenticate_user(self, login_id: str, password: str) -> Optional[Dict[str, Any]]:
        """사용자 인증"""
        try:
            hashed_password = self._hash_password(password)
            
            query = text("""
                SELECT USER_IDX, USER_NAME, LOGIN_FAIL_COUNT, BLOCK_YN
                FROM tbl_user_info 
                WHERE LOGIN_ID = :login_id 
                AND LOGIN_PASSWORD = :password
                AND STATUS_CODE = 'Y'
            """)
            
            result = self.db.execute(query, {
                "login_id": login_id,
                "password": hashed_password
            }).fetchone()
            
            if result:
                # 차단된 사용자 체크
                if result.BLOCK_YN == 'Y':
                    return {"blocked": True}
                
                # 로그인 성공 시 실패 카운트 초기화
                self._reset_login_fail_count(result.USER_IDX)
                
                return {
                    "user_idx": result.USER_IDX,
                    "user_name": result.USER_NAME,
                    "blocked": False
                }
            else:
                # 로그인 실패 시 실패 카운트 증가
                self._increment_login_fail_count(login_id)
                return None
                
        except Exception as e:
            print(f"❌ 사용자 인증 중 오류: {str(e)}")
            traceback.print_exc()
            return None

    def get_user_by_idx(self, user_idx: int) -> Optional[Dict[str, Any]]:
        """사용자 정보 조회"""
        try:
            query = text("""
                SELECT USER_IDX, LOGIN_ID, USER_NAME, BIRTH_DATE, 
                       NICKNAME, EMAIL, USER_DESCRIPTION, MBTI,
                       REG_DATE, UPDATE_DATE
                FROM tbl_user_info 
                WHERE USER_IDX = :user_idx 
                AND STATUS_CODE = 'Y'
            """)
            
            result = self.db.execute(query, {"user_idx": user_idx}).fetchone()
            
            if result:
                return {
                    "user_idx": result.USER_IDX,
                    "login_id": result.LOGIN_ID,
                    "user_name": result.USER_NAME,
                    "birth_date": result.BIRTH_DATE,
                    "nickname": result.NICKNAME,
                    "email": result.EMAIL,
                    "user_description": result.USER_DESCRIPTION,
                    "mbti": result.MBTI,
                    "reg_date": result.REG_DATE,
                    "update_date": result.UPDATE_DATE
                }
            return None
            
        except Exception as e:
            print(f"❌ 사용자 정보 조회 중 오류: {str(e)}")
            traceback.print_exc()
            return None

    def update_user(self, user_idx: int, user_data: Dict[str, Any]) -> bool:
        """사용자 정보 수정"""
        try:
            # 동적 쿼리 생성
            update_fields = []
            params = {"user_idx": user_idx}
            
            if 'user_name' in user_data and user_data['user_name'] is not None:
                update_fields.append("USER_NAME = :user_name")
                params["user_name"] = user_data['user_name']
            
            if 'birth_date' in user_data and user_data['birth_date'] is not None:
                update_fields.append("BIRTH_DATE = :birth_date")
                params["birth_date"] = user_data['birth_date']
            
            if 'nickname' in user_data and user_data['nickname'] is not None:
                update_fields.append("NICKNAME = :nickname")
                params["nickname"] = user_data['nickname']
            
            if 'email' in user_data and user_data['email'] is not None:
                update_fields.append("EMAIL = :email")
                params["email"] = user_data['email']
            
            if 'user_description' in user_data and user_data['user_description'] is not None:
                update_fields.append("USER_DESCRIPTION = :user_description")
                params["user_description"] = user_data['user_description']
            
            if 'mbti' in user_data and user_data['mbti'] is not None:
                update_fields.append("MBTI = :mbti")
                params["mbti"] = user_data['mbti']
            
            if not update_fields:
                return True  # 수정할 내용이 없으면 성공으로 간주
            
            # UPDATE_DATE 추가
            update_fields.append("UPDATE_DATE = NOW()")
            
            query = text(f"""
                UPDATE tbl_user_info 
                SET {', '.join(update_fields)}
                WHERE USER_IDX = :user_idx 
                AND STATUS_CODE = 'Y'
            """)
            
            result = self.db.execute(query, params)
            self.db.commit()
            
            return result.rowcount > 0
            
        except Exception as e:
            print(f"❌ 사용자 정보 수정 중 오류: {str(e)}")
            traceback.print_exc()
            self.db.rollback()
            return False
    
    def _hash_password(self, password: str) -> str:
        """비밀번호 해싱"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _reset_login_fail_count(self, user_idx: int):
        """로그인 실패 카운트 초기화"""
        try:
            query = text("""
                UPDATE tbl_user_info 
                SET LOGIN_FAIL_COUNT = 0 
                WHERE USER_IDX = :user_idx
            """)
            self.db.execute(query, {"user_idx": user_idx})
            self.db.commit()
        except Exception as e:
            print(f"❌ 로그인 실패 카운트 초기화 중 오류: {str(e)}")
    
    def _increment_login_fail_count(self, login_id: str):
        """로그인 실패 카운트 증가"""
        try:
            query = text("""
                UPDATE tbl_user_info 
                SET LOGIN_FAIL_COUNT = LOGIN_FAIL_COUNT + 1 
                WHERE LOGIN_ID = :login_id 
                AND STATUS_CODE = 'Y'
            """)
            self.db.execute(query, {"login_id": login_id})
            self.db.commit()
        except Exception as e:
            print(f"❌ 로그인 실패 카운트 증가 중 오류: {str(e)}")