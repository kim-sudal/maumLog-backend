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
                # 조건이 있을 때: JSON 형식으로 여러 응답 생성
                base_content += self._build_conditions_content(valid_conditions)
            else:
                # 조건이 비어있을 때: 일반 응답 규칙 적용
                base_content += self._get_general_response_rules()
        else:
            # 조건이 None일 때: 일반 응답 규칙 적용
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
            '  "base_response": "🚨 핵심 기본응답 🚨 - 일기 내용을 둥글둥글하게 요약만 하세요 (50-150자, 해시태그 2개 이상 필수, 위로/공감/격려 절대금지)",\n'
        )
        
        for i, condition in enumerate(conditions, 1):
            content += f'  "condition{i}_response": "{condition} 조건을 적용한 응답",\n'
        
        content = content.rstrip(',\n') + "\n}\n\n"
        
        # base_response에 대한 엄격한 규칙 명시
        content += "🚨 base_response 작성 규칙 (절대 준수) 🚨:\n"
        content += """이것이 ai_response로 사용되는 핵심 응답입니다!
- 일기 내용을 둥글둥글하고 부드럽게 요약만 하세요
- 🚫 절대 금지: 위로, 공감, 격려, 조언, "~했을 것 같아요", "~하셨네요"
- 50자이상 150자 내로 순수 요약만
- 구체적인 내용(장소, 사람, 활동, 감정) 포함
- 응답 끝에 해시태그 2개 이상 필수
- 🚫 절대 금지: 인사말, 질문, 마무리 인사

올바른 예시: "흐린 날씨로 기분이 가라앉았지만 따뜻한 커피로 하루를 시작했습니다. 산책을 통해 마음을 차분하게 가라앉히고 작은 일에도 감사함을 느끼려 노력했네요. #흐린날씨 #커피 #산책 #감사함"

❌ 잘못된 예시: "이런 날도 있으니까요. 오늘 하루는 잘 마무리하고..." (이건 위로임)

"""
        
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
            "   - 노래 추천 요청 → 오직 추천 노래는 반드시 Spotify 링크로 (다른 말 절대 금지)\n"
            "   - 감정스코어 요청 → 오직 '숫자/100' 형태로만 (다른 말 절대 금지)\n"
            "   - MBTI 위로 요청 → MBTI 유형이 포함되어 있으면 해당 유형 특성에 맞는 위로, MBTI가 없으면 일반적인 따뜻한 위로\n"
            "   - 감정코드 분석 → 아래 감정코드 중 선택하여 영어값만 하나만 반환\n"
            "   - 기타 모든 요청 → 답변만\n\n"
            "🎭 감정온도 기준 (0-100):\n"
            "- 0~39: 감정에 위로가 필요한 경우 (슬픔, 화남, 불안, 우울 등)\n"
            "- 40~79: 감정이 그럭저럭인데 변화가 필요한 경우 (피곤, 평온 등)\n"
            "- 80~100: 감정이 좋은 날 (기쁨, 행복, 뿌듯 등)\n\n"
            "🎭 감정코드 매핑:\n"
            "{\n" + emotion_codes_str + "\n}\n\n"
            "🚨금지 단어들🚨 (#maum 없을 때):\n"
            "축하합니다, 추천드릴게요, ~입니다, ~네요, ~어떨까요, 완벽한, 자신감에 가득 찬\n\n"
            "✅올바른 예시:\n"
            "노래 추천 요청 → 오직 'https://open.spotify.com/track/곡ID' 형태의 링크만 (다른 말 절대 금지)\n"
            "감정스코어 → '70/100'\n"
            "감정코드 → 'CM'\n"
            "MBTI 위로 → MBTI 있음: 'ENFP라서 새로운 사람들과의 만남이 정말 즐거웠을 것 같아요. 당신의 밝은 에너지가 모든 순간을 특별하게 만들었겠네요!' / MBTI 없음: '오늘 하루도 정말 수고 많으셨어요. 소중한 시간들이 마음 깊이 남을 거예요'\n\n"
            "❌잘못된 예시:\n"
            "'기쁨 감정이므로 JP코드를 추천드릴게요'\n"
            "'70/100! 완벽한 발표였나봐요'\n\n"
            "JSON 형식 외의 다른 텍스트는 절대 포함하지 마세요.\n"
        )
    
    def _get_general_response_rules(self) -> str:
        """일반 응답 규칙"""
        return """반드시 지켜야 할 응답 방식:
- 일기 내용을 둥글둥글하고 부드럽게 요약만 하세요
- 위로, 공감, 격려, 조언은 하지 마세요
- 질문하거나 추가 정보를 요구하지 마세요
- 비속어나 부적절한 표현은 절대 사용하지 마세요

응답 형식:
- 일기 내용의 핵심을 50자이상 150자 내로 둥글둥글하게 요약만 하세요
- 요약에는 일기의 구체적인 내용(장소, 사람, 활동, 감정) 포함되어야 합니다
- 핵심 키워드는 해시태그 형식으로 붙이세요 (예: #직장동료와의식사 #프로젝트완료 #뿌듯함)
- 해시태그는 오늘 일기 내용의 핵심을 나타내며 무조건 응답 끝에 2개이상 있어야합니다
- 해시태그는 구체적인 활동, 장소, 사람, 감정을 포함해야 합니다
- 인사말, 질문, 마무리 인사, 조언, 위로, 공감 금지
- 오직 요약만 둥글둥글하게 작성
- 비속어나 부적절한 표현 절대 금지

예시:
일기: "오늘 회사에서 중요한 프레젠테이션을 했는데 팀장님이 칭찬해주셔서 정말 기뻤어요. 동료들과 회식도 하고 즐거운 하루였습니다."
응답: "회사에서 중요한 프레젠테이션을 진행하고 팀장님께 좋은 평가를 받았네요. 이후 동료들과 함께 회식 시간을 가지며 즐겁게 하루를 마무리했습니다. #프레젠테이션 #팀장칭찬 #동료회식 #기쁨"""

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