from sqlalchemy import text
from .vo import DiaryVO, DiaryCreateRequest, DiaryUpdateRequest
from ..common.encryption_service import EncryptionService
from typing import List, Dict, Any, Tuple, Optional, Union
from datetime import datetime
import traceback

class EmotionDiaryRepository:
    def __init__(self, db):
        self.db = db
        # 암복호화 서비스 초기화
        self.enc = EncryptionService()
    
    def create(self, vo: DiaryCreateRequest) -> int:
        """감정일기 생성 (암복호화 적용)"""
        try:
            sql = text("""
                INSERT INTO tbl_emotion_diary (
                    USER_IDX, 
                    DIARY_CONTENT, 
                    AI_RESPONSE,
                    AI_SELECT, 
                    CONDITION1, CONDITION2, CONDITION3, CONDITION4, CONDITION5, CONDITION6,
                    CONDITION1_RESPONSE, CONDITION2_RESPONSE, CONDITION3_RESPONSE, 
                    CONDITION4_RESPONSE, CONDITION5_RESPONSE,
                    AI_MODEL, RECORD_DATE, REG_DATE, STATUS_CODE
                ) VALUES (
                    :user_idx,
                    fn_enc(:diary_content, :encryption_key),
                    fn_enc(:ai_response, :encryption_key),
                    :ai_select,
                    :condition1, :condition2, :condition3, :condition4, :condition5, :condition6,
                    fn_enc(:condition1_response, :encryption_key),
                    fn_enc(:condition2_response, :encryption_key),
                    fn_enc(:condition3_response, :encryption_key),
                    fn_enc(:condition4_response, :encryption_key),
                    fn_enc(:condition5_response, :encryption_key),
                    :ai_model, :record_date, NOW(), 'Y'
                )
            """)
            
            params = vo.dict()
            
            # 🔥 문제점 1 수정: 이중 암호화에서 단일 암호화로 변경
            # MySQL fn_enc()만 사용 (DB 레벨 암호화)
            
            # 응답값 매핑 (기존 로직 유지)
            if 'condition4_response' in params:
                params['ai_select'] = params.pop('condition4_response')
            elif 'condition4' in params:
                params['ai_select'] = params.pop('condition4')
            
            if 'condition5_response' in params:
                params['condition4_response'] = params.pop('condition5_response')
            
            if 'condition6_response' in params:
                params['condition5_response'] = params.pop('condition6_response')
            
            # 🔥 문제점 2 수정: 원본 데이터를 DB 함수로만 암호화
            params.update({
                'diary_content': params.get('content', ''),  # 원본 텍스트
                'ai_response': params.get('ai_response', ''),  # 원본 텍스트
                'encryption_key': self.enc.get_encryption_key()
            })
            
            # 기본값 설정
            if not params.get('record_date'):
                params['record_date'] = datetime.now()
            
            # 🔥 문제점 3 수정: 응답들도 원본 텍스트로 전달
            # Python 암호화 제거, MySQL 함수에서만 암호화
            
            # 누락된 필드들 기본값 설정
            params.setdefault('condition1', None)
            params.setdefault('condition2', None)
            params.setdefault('condition3', None)
            params.setdefault('condition4', None)
            params.setdefault('condition5', None)
            params.setdefault('condition6', None)
            params.setdefault('condition1_response', None)
            params.setdefault('condition2_response', None)
            params.setdefault('condition3_response', None)
            params.setdefault('condition4_response', None)
            params.setdefault('condition5_response', None)
            params.setdefault('ai_model', None)
            
            result = self.db.execute(sql, params)
            self.db.commit()
            
            print(f"✅ 암호화된 감정일기 저장 완료 (ID: {result.lastrowid})")
            return result.lastrowid
            
        except Exception as e:
            print(f"❌ 암호화된 감정일기 생성 중 오류: {str(e)}")
            traceback.print_exc()
            self.db.rollback()
            raise
    
    def get(self, diary_idx: int) -> Optional[dict]:
        """일기 조회 (복호화 적용)"""
        try:
            sql = text("""
                SELECT 
                    DIARY_IDX, USER_IDX,
                    fn_dec(DIARY_CONTENT, :encryption_key) as DIARY_CONTENT,
                    fn_dec(AI_RESPONSE, :encryption_key) as AI_RESPONSE,
                    AI_SELECT,
                    CONDITION1, CONDITION2, CONDITION3, CONDITION4, CONDITION5, CONDITION6,
                    fn_dec(CONDITION1_RESPONSE, :encryption_key) as CONDITION1_RESPONSE,
                    fn_dec(CONDITION2_RESPONSE, :encryption_key) as CONDITION2_RESPONSE,
                    fn_dec(CONDITION3_RESPONSE, :encryption_key) as CONDITION3_RESPONSE,
                    fn_dec(CONDITION4_RESPONSE, :encryption_key) as CONDITION4_RESPONSE,
                    fn_dec(CONDITION5_RESPONSE, :encryption_key) as CONDITION5_RESPONSE,
                    AI_MODEL, STATUS_CODE, REG_DATE, UPDATE_DATE, RECORD_DATE
                FROM tbl_emotion_diary 
                WHERE DIARY_IDX = :diary_idx AND STATUS_CODE = 'Y'
            """)
            
            params = {
                'diary_idx': diary_idx,
                'encryption_key': self.enc.get_encryption_key()
            }
            
            result = self.db.execute(sql, params).fetchone()
            
            if result:
                # 🔥 문제점 4 수정: 이중 복호화 제거
                # MySQL fn_dec()에서 이미 복호화된 데이터이므로 추가 복호화 불필요
                
                return {
                    "diary_idx": result.DIARY_IDX,
                    "user_idx": result.USER_IDX,
                    "content": result.DIARY_CONTENT or "",  # 이미 복호화된 데이터
                    "condition1": result.CONDITION1,
                    "condition2": result.CONDITION2,
                    "condition3": result.CONDITION3,
                    "condition4": result.CONDITION4,
                    "condition5": result.CONDITION5,
                    "condition6": result.CONDITION6,
                    "ai_select": result.AI_SELECT,
                    "condition1_response": result.CONDITION1_RESPONSE or "",  # 이미 복호화됨
                    "condition2_response": result.CONDITION2_RESPONSE or "",  # 이미 복호화됨
                    "condition3_response": result.CONDITION3_RESPONSE or "",  # 이미 복호화됨
                    "condition4_response": result.AI_SELECT,  # 기존 매핑 유지
                    "condition5_response": result.CONDITION4_RESPONSE or "",  # 이미 복호화됨
                    "condition6_response": result.CONDITION5_RESPONSE or "",  # 이미 복호화됨
                    "ai_response": result.AI_RESPONSE or "",  # 이미 복호화된 데이터
                    "ai_model": result.AI_MODEL,
                    "status_code": result.STATUS_CODE,
                    "reg_date": result.REG_DATE,
                    "update_date": result.UPDATE_DATE,
                    "record_date": result.RECORD_DATE
                }
            return None
            
        except Exception as e:
            print(f"❌ 암호화된 감정일기 조회 중 오류: {str(e)}")
            traceback.print_exc()
            raise
    
    def get_list(self, user_idx: int = None, start_date: str = None, page: int = 1, page_size: int = 10) -> Tuple[List[dict], int]:
        """일기 목록 조회 (복호화 적용)"""
        try:
            # 기본 WHERE 조건
            where_conditions = ["STATUS_CODE = 'Y'"]
            params = {'encryption_key': self.enc.get_encryption_key()}
            
            # 사용자 필터
            if user_idx:
                where_conditions.append("USER_IDX = :user_idx")
                params["user_idx"] = user_idx
            
            # 월별 필터 추가
            if start_date:
                where_conditions.append("DATE_FORMAT(RECORD_DATE, '%Y-%m') = :start_date")
                params["start_date"] = start_date
                        
            where_clause = " AND ".join(where_conditions)
            
            # 전체 개수 조회
            count_sql = text(f"SELECT COUNT(*) as total FROM tbl_emotion_diary WHERE {where_clause}")
            count_result = self.db.execute(count_sql, {k: v for k, v in params.items() if k != 'encryption_key'}).fetchone()
            total_count = count_result.total if count_result else 0
            
            # 목록 조회 (페이징)
            offset = (page - 1) * page_size
            params.update({"limit": page_size, "offset": offset})
            
            list_sql = text(f"""
                SELECT 
                    DIARY_IDX, USER_IDX,
                    fn_dec(DIARY_CONTENT, :encryption_key) as DIARY_CONTENT,
                    fn_dec(AI_RESPONSE, :encryption_key) as AI_RESPONSE,
                    CONDITION1, CONDITION2, CONDITION3, CONDITION4, CONDITION5, CONDITION6,
                    fn_dec(CONDITION1_RESPONSE, :encryption_key) as CONDITION1_RESPONSE,
                    fn_dec(CONDITION2_RESPONSE, :encryption_key) as CONDITION2_RESPONSE,
                    fn_dec(CONDITION3_RESPONSE, :encryption_key) as CONDITION3_RESPONSE,
                    fn_dec(CONDITION4_RESPONSE, :encryption_key) as CONDITION4_RESPONSE,
                    fn_dec(CONDITION5_RESPONSE, :encryption_key) as CONDITION5_RESPONSE,
                    AI_SELECT, AI_MODEL, RECORD_DATE, UPDATE_DATE, STATUS_CODE
                FROM tbl_emotion_diary 
                WHERE {where_clause}
                ORDER BY RECORD_DATE DESC, DIARY_IDX DESC
                LIMIT :limit OFFSET :offset
            """)
            
            result = self.db.execute(list_sql, params).fetchall()
            
            # 🔥 문제점 5 수정: 이중 복호화 제거
            diaries = []
            for row in result:
                diary = {
                    'diary_idx': row.DIARY_IDX,
                    'user_idx': row.USER_IDX,
                    'content': row.DIARY_CONTENT or "",  # 이미 복호화됨
                    'ai_response': row.AI_RESPONSE or "",  # 이미 복호화됨
                    'condition1': row.CONDITION1,
                    'condition1_response': row.CONDITION1_RESPONSE or "",  # 이미 복호화됨
                    'condition2': row.CONDITION2,
                    'condition2_response': row.CONDITION2_RESPONSE or "",  # 이미 복호화됨
                    'condition3': row.CONDITION3,
                    'condition3_response': row.CONDITION3_RESPONSE or "",  # 이미 복호화됨
                    'condition4': row.CONDITION4,
                    'condition4_response': row.AI_SELECT,  # 기존 매핑 유지
                    'condition5': row.CONDITION5,
                    'condition5_response': row.CONDITION4_RESPONSE or "",  # 이미 복호화됨
                    'condition6': row.CONDITION6,
                    'condition6_response': row.CONDITION5_RESPONSE or "",  # 이미 복호화됨
                    'ai_model': row.AI_MODEL,
                    'record_date': row.RECORD_DATE.isoformat() if row.RECORD_DATE else None,
                    'update_date': row.UPDATE_DATE.isoformat() if row.UPDATE_DATE else None,
                    'status_code': row.STATUS_CODE
                }
                diaries.append(diary)
            
            print(f"✅ 암호화된 일기 목록 조회 완료 ({len(diaries)}건)")
            return diaries, total_count
            
        except Exception as e:
            print(f"❌ 암호화된 일기 목록 조회 중 오류: {str(e)}")
            traceback.print_exc()
            return [], 0
 
    def update(self, diary_idx: int, vo: DiaryUpdateRequest) -> bool:
        """감정일기 수정 (암복호화 적용)"""
        try:
            # 존재하는 일기인지 확인
            existing = self.get(diary_idx)
            if not existing:
                return False
            
            # 동적 쿼리 생성
            update_fields = []
            params = {
                "diary_idx": diary_idx, 
                "encryption_key": self.enc.get_encryption_key()
            }
            
            vo_dict = vo.dict(exclude_unset=True, exclude={'diary_idx'})
            
            # 🔥 수정 1: 내용 수정 시 단일 암호화
            if 'content' in vo_dict:
                update_fields.append("DIARY_CONTENT = fn_enc(:content, :encryption_key)")
                params["content"] = vo_dict['content']  # 원본 텍스트
            
            # AI 응답 수정 시 단일 암호화
            if 'ai_response' in vo_dict:
                update_fields.append("AI_RESPONSE = fn_enc(:ai_response, :encryption_key)")
                params["ai_response"] = vo_dict['ai_response']  # 원본 텍스트
            
            # 🔥 수정 2: 응답값 매핑 처리 (순서 중요!)
            # condition1~3_response는 먼저 처리
            for i in range(1, 4):
                response_field = f'condition{i}_response'
                if response_field in vo_dict:
                    update_fields.append(f"CONDITION{i}_RESPONSE = fn_enc(:{response_field}, :encryption_key)")
                    params[response_field] = vo_dict[response_field]  # 원본 텍스트
            
            # condition4_response -> AI_SELECT 매핑
            if 'condition4_response' in vo_dict:
                update_fields.append("AI_SELECT = :ai_select")
                params["ai_select"] = vo_dict['condition4_response']
            
            # condition5_response -> CONDITION4_RESPONSE 매핑
            if 'condition5_response' in vo_dict:
                update_fields.append("CONDITION4_RESPONSE = fn_enc(:condition4_response_mapped, :encryption_key)")
                params["condition4_response_mapped"] = vo_dict['condition5_response']  # 원본 텍스트
            
            # condition6_response -> CONDITION5_RESPONSE 매핑
            if 'condition6_response' in vo_dict:
                update_fields.append("CONDITION5_RESPONSE = fn_enc(:condition5_response_mapped, :encryption_key)")
                params["condition5_response_mapped"] = vo_dict['condition6_response']  # 원본 텍스트
            
            # 🔥 수정 3: 조건들은 암호화하지 않음
            for i in range(1, 7):
                condition_field = f'condition{i}'
                if condition_field in vo_dict:
                    update_fields.append(f"CONDITION{i} = :{condition_field}")
                    params[condition_field] = vo_dict[condition_field]
            
            # 기타 필드들
            if 'ai_model' in vo_dict:
                update_fields.append("AI_MODEL = :ai_model")
                params["ai_model"] = vo_dict['ai_model']
            
            if 'record_date' in vo_dict:
                update_fields.append("RECORD_DATE = :record_date")
                params["record_date"] = vo_dict['record_date']
            
            # 🔥 수정 4: 업데이트할 필드가 없으면 성공으로 처리
            if not update_fields:
                print(f"✅ 수정할 필드가 없음 (ID: {diary_idx})")
                return True
            
            # UPDATE_DATE는 항상 추가
            update_fields.append("UPDATE_DATE = NOW()")
            
            # 🔥 수정 5: SQL 쿼리 정리
            sql = text(f"""
                UPDATE tbl_emotion_diary 
                SET {', '.join(update_fields)}
                WHERE DIARY_IDX = :diary_idx AND STATUS_CODE = 'Y'
            """)
            
            print(f"🔍 실행할 SQL: {sql}")
            print(f"🔍 파라미터: {params}")
            
            result = self.db.execute(sql, params)
            self.db.commit()
            
            print(f"✅ 암호화된 감정일기 수정 완료 (ID: {diary_idx}, 영향받은 행: {result.rowcount})")
            return result.rowcount > 0
            
        except Exception as e:
            print(f"❌ 암호화된 감정일기 수정 중 오류: {str(e)}")
            print(f"❌ vo_dict: {vo.dict() if vo else 'None'}")
            traceback.print_exc()
            self.db.rollback()
            raise
    
    def delete(self, diary_idx: int) -> bool:
        """감정일기 삭제 (논리삭제)"""
        try:
            sql = text("""
                UPDATE tbl_emotion_diary 
                SET STATUS_CODE = 'N', UPDATE_DATE = NOW()
                WHERE DIARY_IDX = :diary_idx AND STATUS_CODE = 'Y'
            """)
            
            result = self.db.execute(sql, {"diary_idx": diary_idx})
            self.db.commit()
            
            print(f"✅ 감정일기 삭제 완료 (ID: {diary_idx})")
            return result.rowcount > 0
            
        except Exception as e:
            print(f"❌ 감정일기 삭제 중 오류: {str(e)}")
            traceback.print_exc()
            self.db.rollback()
            raise
