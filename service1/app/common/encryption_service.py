import os
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import hashlib

class EncryptionService:
    """통합 암복호화 서비스"""
    
    def __init__(self):
        # 환경변수에서 통합 암호화 키 로드
        self.encryption_key = os.getenv("ENCRYPTION_KEY")
        
        # 키 검증
        self._validate_key()
        
        # Fernet 암호화 객체 생성
        self.cipher = self._create_cipher(self.encryption_key)
    
    def _validate_key(self):
        """암호화 키 유효성 검증"""
        if not self.encryption_key:
            raise ValueError("❌ ENCRYPTION_KEY가 환경변수에 설정되지 않았습니다.")
        if len(self.encryption_key) < 32:
            raise ValueError("❌ ENCRYPTION_KEY는 최소 32자 이상이어야 합니다.")
        
        print("✅ 통합 암호화 키가 정상적으로 로드되었습니다.")
    
    def _create_cipher(self, password: str) -> Fernet:
        """패스워드로부터 Fernet 암호화 객체 생성"""
        # 솔트 생성 (고정값 사용하여 일관성 유지)
        salt = hashlib.sha256(password.encode()).digest()[:16]
        
        # PBKDF2로 키 유도
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """데이터 암호화 (모든 종류의 데이터에 공통 사용)"""
        if not data:
            return data
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """데이터 복호화 (모든 종류의 데이터에 공통 사용)"""
        if not encrypted_data:
            return encrypted_data
        try:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            print(f"⚠️ 데이터 복호화 실패: {e}")
            return encrypted_data
    
    def get_encryption_key(self) -> str:
        """DB 함수용 암호화 키 반환"""
        return self.encryption_key