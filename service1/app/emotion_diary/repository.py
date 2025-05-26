from sqlalchemy import text
from .vo import DiaryVO, DiaryCreateRequest, DiaryUpdateRequest
from typing import List, Dict, Any, Tuple, Optional, Union
from datetime import datetime
import traceback

class EmotionDiaryRepository:
    def __init__(self, db):
        self.db = db
    
    def create(self, vo: DiaryCreateRequest) -> int:
        """감정일기 생성"""
        try:
            sql = text("""
                INSERT INTO tbl_emotion_diary (
                    USER_IDX, DIARY_CONTENT, AI_SELECT, CONDITION1, CONDITION2, CONDITION3,
                    CONDITION1_RESPONSE, CONDITION2_RESPONSE, CONDITION3_RESPONSE, AI_RESPONSE,
                    AI_MODEL, RECORD_DATE, REG_DATE, STATUS_CODE
                ) VALUES (
                    :user_idx, :content, :ai_select, :condition1, :condition2, :condition3,
                    :condition1_response, :condition2_response, :condition3_response, :ai_response,
                    :ai_model, :record_date, NOW(), 'Y'
                )
            """)
            
            params = vo.dict()
            
            # condition4_response를 ai_select로 매핑 (DB의 AI_SELECT 컬럼에 저장)
            if 'condition4_response' in params:
                params['ai_select'] = params.pop('condition4_response')
            elif 'condition4' in params:
                params['ai_select'] = params.pop('condition4')
            
            # 기본값 설정
            if not params.get('record_date'):
                params['record_date'] = datetime.now()
            
            # 누락된 필드들 기본값 설정
            params.setdefault('condition1_response', None)
            params.setdefault('condition2_response', None)
            params.setdefault('condition3_response', None)
            params.setdefault('ai_response', None)
            params.setdefault('ai_model', None)
            
            result = self.db.execute(sql, params)
            self.db.commit()
            return result.lastrowid
            
        except Exception as e:
            print(f"❌ 감정일기 생성 중 오류: {str(e)}")
            traceback.print_exc()
            self.db.rollback()
            raise
    
    def get(self, diary_idx: int) -> Optional[dict]:
        """일기 조회"""
        try:
            sql = text("""
                SELECT DIARY_IDX, USER_IDX, DIARY_CONTENT, AI_SELECT, 
                       CONDITION1, CONDITION2, CONDITION3,
                       CONDITION1_RESPONSE, CONDITION2_RESPONSE, CONDITION3_RESPONSE,
                       AI_RESPONSE, AI_MODEL, STATUS_CODE, REG_DATE, UPDATE_DATE, RECORD_DATE
                FROM tbl_emotion_diary 
                WHERE DIARY_IDX = :diary_idx AND STATUS_CODE = 'Y'
            """)
            
            result = self.db.execute(sql, {"diary_idx": diary_idx}).fetchone()
            
            if result:
                return {
                    "diary_idx": result.DIARY_IDX,
                    "user_idx": result.USER_IDX,
                    "content": result.DIARY_CONTENT,
                    "condition1": result.CONDITION1,
                    "condition2": result.CONDITION2,
                    "condition3": result.CONDITION3,
                    "ai_select": result.AI_SELECT,  # condition4_response 값이 저장됨
                    "condition1_response": result.CONDITION1_RESPONSE,
                    "condition2_response": result.CONDITION2_RESPONSE,
                    "condition3_response": result.CONDITION3_RESPONSE,
                    "ai_response": result.AI_RESPONSE,
                    "ai_model": result.AI_MODEL,
                    "status_code": result.STATUS_CODE,
                    "reg_date": result.REG_DATE,
                    "update_date": result.UPDATE_DATE,
                    "record_date": result.RECORD_DATE
                }
            return None
            
        except Exception as e:
            print(f"❌ 감정일기 조회 중 오류: {str(e)}")
            traceback.print_exc()
            raise
    
    def update(self, diary_idx: int, vo: DiaryUpdateRequest) -> bool:
        """감정일기 수정"""
        try:
            # 존재하는 일기인지 확인
            existing = self.get(diary_idx)
            if not existing:
                return False
            
            # 동적 쿼리 생성
            update_fields = []
            params = {"diary_idx": diary_idx, "update_date": datetime.now()}
            
            vo_dict = vo.dict(exclude_unset=True, exclude={'diary_idx'})
            
            if 'content' in vo_dict:
                update_fields.append("DIARY_CONTENT = :content")
                params["content"] = vo_dict['content']
            
            # condition4_response를 ai_select로 처리 (DB의 AI_SELECT 컬럼에 저장)
            if 'condition4_response' in vo_dict:
                update_fields.append("AI_SELECT = :ai_select")
                params["ai_select"] = vo_dict['condition4_response']
            elif 'condition4' in vo_dict:
                update_fields.append("AI_SELECT = :ai_select")
                params["ai_select"] = vo_dict['condition4']
            elif 'ai_select' in vo_dict:
                update_fields.append("AI_SELECT = :ai_select")
                params["ai_select"] = vo_dict['ai_select']
            
            if 'condition1' in vo_dict:
                update_fields.append("CONDITION1 = :condition1")
                params["condition1"] = vo_dict['condition1']
            
            if 'condition2' in vo_dict:
                update_fields.append("CONDITION2 = :condition2")
                params["condition2"] = vo_dict['condition2']
            
            if 'condition3' in vo_dict:
                update_fields.append("CONDITION3 = :condition3")
                params["condition3"] = vo_dict['condition3']
            
            # 응답 필드들 추가
            if 'condition1_response' in vo_dict:
                update_fields.append("CONDITION1_RESPONSE = :condition1_response")
                params["condition1_response"] = vo_dict['condition1_response']
            
            if 'condition2_response' in vo_dict:
                update_fields.append("CONDITION2_RESPONSE = :condition2_response")
                params["condition2_response"] = vo_dict['condition2_response']
            
            if 'condition3_response' in vo_dict:
                update_fields.append("CONDITION3_RESPONSE = :condition3_response")
                params["condition3_response"] = vo_dict['condition3_response']
            
            if 'ai_response' in vo_dict:
                update_fields.append("AI_RESPONSE = :ai_response")
                params["ai_response"] = vo_dict['ai_response']
            
            if 'ai_model' in vo_dict:
                update_fields.append("AI_MODEL = :ai_model")
                params["ai_model"] = vo_dict['ai_model']
            
            if 'record_date' in vo_dict:
                update_fields.append("RECORD_DATE = :record_date")
                params["record_date"] = vo_dict['record_date']
            
            if not update_fields:
                return True
            
            update_fields.append("UPDATE_DATE = :update_date")
            sql = text(f"""
                UPDATE tbl_emotion_diary 
                SET {', '.join(update_fields)}
                WHERE DIARY_IDX = :diary_idx AND STATUS_CODE = 'Y'
            """)
            
            result = self.db.execute(sql, params)
            self.db.commit()
            return result.rowcount > 0
            
        except Exception as e:
            print(f"❌ 감정일기 수정 중 오류: {str(e)}")
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
            return result.rowcount > 0
            
        except Exception as e:
            print(f"❌ 감정일기 삭제 중 오류: {str(e)}")
            traceback.print_exc()
            self.db.rollback()
            raise
    
    def get_list(self, user_idx: int = None, page: int = 1, page_size: int = 10) -> Tuple[List[dict], int]:
        """일기 목록 조회"""
        try:
            # 전체 개수 조회
            if user_idx:
                count_sql = text("SELECT COUNT(*) as total FROM tbl_emotion_diary WHERE USER_IDX = :user_idx AND STATUS_CODE = 'Y'")
                count_params = {"user_idx": user_idx}
            else:
                count_sql = text("SELECT COUNT(*) as total FROM tbl_emotion_diary WHERE STATUS_CODE = 'Y'")
                count_params = {}
            
            count_result = self.db.execute(count_sql, count_params).fetchone()
            total_count = count_result.total if count_result else 0
            
            # 데이터 조회
            offset = (page - 1) * page_size
            
            if user_idx:
                data_sql = text("""
                    SELECT DIARY_IDX, USER_IDX, DIARY_CONTENT, AI_SELECT, 
                           CONDITION1, CONDITION2, CONDITION3,
                           CONDITION1_RESPONSE, CONDITION2_RESPONSE, CONDITION3_RESPONSE,
                           AI_RESPONSE, AI_MODEL, STATUS_CODE, REG_DATE, UPDATE_DATE, RECORD_DATE
                    FROM tbl_emotion_diary 
                    WHERE USER_IDX = :user_idx AND STATUS_CODE = 'Y'
                    ORDER BY RECORD_DATE DESC 
                    LIMIT :limit OFFSET :offset
                """)
                data_params = {"user_idx": user_idx, "limit": page_size, "offset": offset}
            else:
                data_sql = text("""
                    SELECT DIARY_IDX, USER_IDX, DIARY_CONTENT, AI_SELECT, 
                           CONDITION1, CONDITION2, CONDITION3,
                           CONDITION1_RESPONSE, CONDITION2_RESPONSE, CONDITION3_RESPONSE,
                           AI_RESPONSE, AI_MODEL, STATUS_CODE, REG_DATE, UPDATE_DATE, RECORD_DATE
                    FROM tbl_emotion_diary 
                    WHERE STATUS_CODE = 'Y'
                    ORDER BY RECORD_DATE DESC 
                    LIMIT :limit OFFSET :offset
                """)
                data_params = {"limit": page_size, "offset": offset}
            
            results = self.db.execute(data_sql, data_params).fetchall()
            
            diaries = []
            for result in results:
                diaries.append({
                    "diary_idx": result.DIARY_IDX,
                    "user_idx": result.USER_IDX,
                    "content": result.DIARY_CONTENT,
                    "condition1": result.CONDITION1,
                    "condition2": result.CONDITION2,
                    "condition3": result.CONDITION3,
                    "ai_select": result.AI_SELECT,  # condition4_response 값이 저장됨
                    "condition1_response": result.CONDITION1_RESPONSE,
                    "condition2_response": result.CONDITION2_RESPONSE,
                    "condition3_response": result.CONDITION3_RESPONSE,
                    "ai_response": result.AI_RESPONSE,
                    "ai_model": result.AI_MODEL,
                    "status_code": result.STATUS_CODE,
                    "reg_date": result.REG_DATE,
                    "update_date": result.UPDATE_DATE,
                    "record_date": result.RECORD_DATE
                })
            
            return diaries, total_count
            
        except Exception as e:
            print(f"❌ 감정일기 목록 조회 중 오류: {str(e)}")
            traceback.print_exc()
            raise
    
    def get_by_date_range(self, user_idx: int, start_date: datetime, end_date: datetime) -> List[dict]:
        """날짜 범위로 일기 조회"""
        try:
            sql = text("""
                SELECT DIARY_IDX, USER_IDX, DIARY_CONTENT, AI_SELECT, 
                       CONDITION1, CONDITION2, CONDITION3,
                       CONDITION1_RESPONSE, CONDITION2_RESPONSE, CONDITION3_RESPONSE,
                       AI_RESPONSE, AI_MODEL, STATUS_CODE, REG_DATE, UPDATE_DATE, RECORD_DATE
                FROM tbl_emotion_diary 
                WHERE USER_IDX = :user_idx AND STATUS_CODE = 'Y'
                AND RECORD_DATE >= :start_date AND RECORD_DATE <= :end_date
                ORDER BY RECORD_DATE DESC
            """)
            
            results = self.db.execute(sql, {
                "user_idx": user_idx,
                "start_date": start_date,
                "end_date": end_date
            }).fetchall()
            
            diaries = []
            for result in results:
                diaries.append({
                    "diary_idx": result.DIARY_IDX,
                    "user_idx": result.USER_IDX,
                    "content": result.DIARY_CONTENT,
                    "condition1": result.CONDITION1,
                    "condition2": result.CONDITION2,
                    "condition3": result.CONDITION3,
                    "ai_select": result.AI_SELECT,  # condition4_response 값이 저장됨
                    "condition1_response": result.CONDITION1_RESPONSE,
                    "condition2_response": result.CONDITION2_RESPONSE,
                    "condition3_response": result.CONDITION3_RESPONSE,
                    "ai_response": result.AI_RESPONSE,
                    "ai_model": result.AI_MODEL,
                    "status_code": result.STATUS_CODE,
                    "reg_date": result.REG_DATE,
                    "update_date": result.UPDATE_DATE,
                    "record_date": result.RECORD_DATE
                })
            
            return diaries
            
        except Exception as e:
            print(f"❌ 날짜별 감정일기 조회 중 오류: {str(e)}")
            traceback.print_exc()
            raise