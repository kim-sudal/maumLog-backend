from sqlalchemy.orm import Session
import requests
import os
import json
from typing import Dict, Any, List
from .common_vo import ChatGPTRequestVO

class ChatGPTRepository:
    def __init__(self, db: Session):
        self.db = db
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-4-turbo"
        
        # 감정코드 매핑
        self.emotion_codes = {
            "기쁨": "JP",
            "행복": "HP", 
            "뿌듯": "PR",
            "피곤": "TI",
            "슬픔": "SD",
            "화남": "AN",
            "불안": "AX",
            "우울": "DP",
            "평온": "CM"
        }
        
        if self.api_key:
            print(f"✅ ChatGPT API 키 로딩 완료 (길이: {len(self.api_key)})")
        else:
            print("❌ ChatGPT API 키를 찾을 수 없습니다. 환경변수를 확인하세요.")

    def send_prompt(self, vo: ChatGPTRequestVO, conditions: List[str] = None) -> Dict[str, Any]:
        """감정코드 기반 ChatGPT API 요청"""
        if not self.api_key:
            return {
                "error": "OpenAI API 키가 설정되지 않았습니다.",
                "status_code": 500
            }

        system_message = self._build_system_message(conditions)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                system_message,
                {"role": "user", "content": vo.prompt}
            ],
            "max_tokens": vo.max_tokens,
            "temperature": vo.temperature
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            self._log_response(vo.prompt, response.text)
            
            if response.status_code == 200:
                print(f"✅ ChatGPT API 요청 성공")
                api_response = response.json()
                
                if conditions:
                    api_response = self._parse_json_response(api_response)
                
                return api_response
            else:
                print(f"❌ ChatGPT API 오류: {response.status_code}")
                return {
                    "error": f"API 오류: {response.status_code} - {response.text}",
                    "status_code": response.status_code
                }
                
        except Exception as e:
            print(f"❌ ChatGPT API 요청 중 예외 발생: {str(e)}")
            return {"error": str(e), "status_code": 500}

    def _build_system_message(self, conditions: List[str] = None) -> Dict[str, str]:
        """시스템 메시지 구성"""
        base_content = self._get_base_system_content()
        
        if conditions:
            valid_conditions = [cond.strip() for cond in conditions if cond and cond.strip()]
            if valid_conditions:
                base_content += self._build_conditions_content(valid_conditions)
        else:
            base_content += self._get_general_response_rules()
            
        return {"role": "system", "content": base_content}

    def _get_base_system_content(self) -> str:
        """기본 시스템 프롬프트"""
        return (
            "당신은 감정 기반 AI 도우미입니다.\n\n"
            "🚨 절대 규칙 🚨\n"
            "1. 인사말 금지: '안녕하세요', '반갑습니다', '도움이 되었으면 좋겠습니다' 등 절대 사용하지 마세요\n"
            "2. 자기소개 금지: '저는 ~입니다' 같은 자기소개 절대 하지 마세요\n"
            "3. 마무리 인사 금지: '도움이 되셨나요?', '언제든 말씀해주세요' 등 마무리 인사 절대 하지 마세요\n\n"
        )

    def _build_conditions_content(self, conditions: List[str]) -> str:
        """조건별 응답 형식 구성"""
        content = (
            "🔥 중요한 응답 형식 🔥\n"
            "반드시 다음 JSON 형식으로만 응답하세요:\n"
            "{\n"
            '  "base_response": "기본 응답",\n'
        )
        
        for i, condition in enumerate(conditions, 1):
            content += f'  "condition{i}_response": "{condition} 조건을 적용한 응답",\n'
        
        content = content.rstrip(',\n') + "\n}\n\n"
        
        content += "적용할 조건들:\n"
        for i, condition in enumerate(conditions, 1):
            content += f"{i}. {condition}\n"
        
        content += self._get_emotion_response_rules()
        
        return content

    def _get_emotion_response_rules(self) -> str:
        """감정코드 기반 응답 규칙"""
        emotion_codes_str = "\n".join([f'  "{k}": "{v}",' for k, v in self.emotion_codes.items()])
        
        return (
            "\n🎯 감정코드 기반 응답 규칙:\n"
            "조건을 하나씩 확인하세요:\n\n"
            "1️⃣ 조건에 '#maum' 문자가 포함되어 있는가?\n"
            "   YES → 감정일기 도우미로서 따뜻한 공감과 위로로 응답\n"
            "   NO → 아래 2️⃣번으로\n\n"
            "2️⃣ #maum이 없는 조건은 🚨절대 수식어 금지🚨:\n"
            "   - 노래 추천 요청 → 오직 '가수명 - 곡명' (다른 말 절대 금지)\n"
            "   - 감정스코어 요청 → 오직 '숫자/10' (다른 말 절대 금지)\n"
            "   - MBTI 위로 요청 → 핵심 위로만\n"
            "   - 감정코드 분석 → 아래 감정코드 중 선택하여 영어값만 하나만 반환\n"
            "   - 기타 모든 요청 → 답변만\n\n"
            "🎭 감정코드 매핑:\n"
            "{\n" + emotion_codes_str + "\n}\n\n"
            "🚨금지 단어들🚨 (#maum 없을 때):\n"
            "축하합니다, 추천드릴게요, ~입니다, ~네요, ~어떨까요, 완벽한, 자신감에 가득 찬\n\n"
            "✅올바른 예시:\n"
            "노래 추천 → 'IU - 밤편지'\n"
            "감정스코어 → '9/10'\n"
            "감정코드 → 'JP'\n"
            "MBTI 위로 → '목표 달성의 쾌감을 느끼세요'\n\n"
            "❌잘못된 예시:\n"
            "'기쁨 감정이므로 JP코드를 추천드릴게요'\n"
            "'9/10! 완벽한 발표였나봐요'\n\n"
            "JSON 형식 외의 다른 텍스트는 절대 포함하지 마세요.\n"
        )

    def _get_general_response_rules(self) -> str:
        """일반 응답 규칙"""
        return (
            "반드시 지켜야 할 응답 방식:\n"
            "- 사용자의 감정에 바로 공감하며 시작하세요\n"
            "- 따뜻한 위로와 격려의 말로만 응답하세요\n"
            "- 질문하거나 추가 정보를 요구하지 마세요\n"
            "- 조언이나 해결책 제시는 하지 마세요\n"
            "- 비속어나 부적절한 표현은 절대 사용하지 마세요\n"
            "응답 형식: 공감 → 위로 → 격려 (인사말 없이 바로 시작, 마무리 인사 없이 끝)"
        )

    def _parse_json_response(self, api_response: Dict[str, Any]) -> Dict[str, Any]:
        """JSON 응답 파싱"""
        try:
            content = api_response["choices"][0]["message"]["content"]
            parsed_content = json.loads(content)
            api_response["parsed_responses"] = parsed_content
            return api_response
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON 파싱 실패, 원본 응답 반환: {str(e)}")
            return api_response

    def get_emotion_code(self, emotion_name: str) -> str:
        """감정명으로 감정코드 조회"""
        return self.emotion_codes.get(emotion_name, "CM")  # 기본값: 평온

    def get_emotion_name(self, emotion_code: str) -> str:
        """감정코드로 감정명 조회"""
        for name, code in self.emotion_codes.items():
            if code == emotion_code:
                return name
        return "평온"

    def _log_response(self, prompt: str, response: str) -> None:
        """API 요청과 응답을 DB에 로깅"""
        try:
            sql = """
            INSERT INTO chatgpt_logs (prompt, response, created_at)
            VALUES (:prompt, :response, CURRENT_TIMESTAMP)
            """
            self.db.execute(sql, {"prompt": prompt, "response": response})
            self.db.commit()
        except Exception as e:
            print(f"⚠️ API 로그 저장 실패: {str(e)}")
            pass