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
            '  "base_response": "🚨 핵심 기본응답 🚨 - 일기 내용을 둥글둥글하게 요약만 하세요 (50-150자, 해시태그 절대 금지, 위로/공감/격려 절대금지)",\n'
        )
        
        for i, condition in enumerate(conditions, 1):
            content += f'  "condition{i}_response": "{condition} 조건을 적용한 응답",\n'
        
        content = content.rstrip(',\n') + "\n}\n\n"
        
        # base_response에 대한 엄격한 규칙 명시
        content += "🚨 base_response 작성 규칙 (절대 준수) 🚨:\n"
        content += """이것이 ai_response로 사용되는 핵심 응답입니다!
- 일기 내용을 둥글둥글하고 부드럽게 요약만 하세요
- 🚫 절대 금지: 위로, 공감, 격려, 조언, "~했을 것 같아요", "~하셨네요"
- 🚫 절대 금지: 해시태그 (해시태그는 condition6에서 별도 처리)
- 50자이상 150자 내로 순수 요약만
- 구체적인 내용(장소, 사람, 활동, 감정) 포함
- 🚫 절대 금지: 인사말, 질문, 마무리 인사

올바른 예시: "흐린 날씨로 기분이 가라앉았지만 따뜻한 커피로 하루를 시작했습니다. 산책을 통해 마음을 차분하게 가라앉히고 작은 일에도 감사함을 느끼려 노력했네요."

❌ 잘못된 예시: 
- "이런 날도 있으니까요. 오늘 하루는 잘 마무리하고..." (이건 위로임)
- "...산책을 했네요. #산책 #감사함" (해시태그 금지)

"""
        
        content += "적용할 조건들:\n"
        for i, condition in enumerate(conditions, 1):
            content += f"{i}. {condition}\n"
        
        content += self._get_emotion_response_rules()
        
        return content

    def _get_emotion_response_rules(self) -> str:
        """감정코드 기반 응답 규칙"""
        emotion_codes_str = "\n".join([f'  "{k}": "{v}",' for k, v in self.emotion_codes.items()])
        
        return ("""
            감정코드 기반 응답 규칙:
            조건을 하나씩 확인하세요:

            1. 조건에 '#maum' 문자가 포함되어 있는가?
            YES → 감정일기 도우미로서 따뜻한 공감과 위로로 응답
            NO → 아래 2번으로

            2. #maum이 없는 조건은 절대 수식어 금지:
            - market=KR, locale=ko_KR로 Spotify 공식 API에서 한국노래 존재 여부를 반드시 확인할 것  
            - 트랙 ID를 정확히 복사했는지 재확인할 것  
            - URL 형식은 https://open.spotify.com/track/{트랙ID}?si={코드} 이어야 함  
            - 한국노래 트랙 URL 3개 이상 제공할 것  
            - 감정스코어 요청 → 오직 '숫자/100' 형태로만
            - MBTI 위로 요청 → MBTI 유형이 포함되어 있으면 해당 유형 특성에 맞는 위로, MBTI가 없으면 일반적인 따뜻한 위로
            - 감정코드 분석 → 감정코드 중 선택하여 영어값만 하나만 반환
            - 조언 요청 → 따뜻하고 공감적인 조언 제공
            - 해시태그 요청 → 일기 내용의 핵심 키워드를 해시태그 형식으로만 반환 (2개 이상, 설명 금지)
            - 기타 모든 요청 → 답변만

            감정온도 기준 (0-100):
            - 0~39: 감정에 위로가 필요한 경우 (슬픔, 화남, 불안, 우울 등)
            - 40~79: 감정이 그럭저럭인데 변화가 필요한 경우 (피곤, 평온 등)
            - 80~100: 감정이 좋은 날 (기쁨, 행복, 뿌듯 등)

            감정코드 매핑:
            "기쁨": "JP",
            "행복": "HP", 
            "뿌듯": "PR",
            "피곤": "TI",
            "슬픔": "SD",
            "화남": "AN",
            "불안": "AX",
            "우울": "DP",
            "평온": "CM" 중에서만 줘야함

            조언 요청:
            - 일기 내용의 감정 상태를 파악하고 그에 맞는 따뜻한 조언 제공
            - 공감과 위로를 기반으로 한 실질적이고 따뜻한 조언
            - 강요하지 않는 부드러운 톤으로 제안

            해시태그 요청:
            - 일기 내용에서 핵심 키워드만 추출하여 해시태그 형식으로 제공
            - 최소 2개 이상, 최대 6개까지
            - 구체적인 활동, 장소, 사람, 감정 포함
            - 오직 해시태그만, 다른 설명이나 문장 절대 금지
            - 형식: '#키워드1 #키워드2 #키워드3...'

            금지 단어들 (#maum 없을 때):
            축하합니다, 추천드릴게요, ~입니다, ~네요, ~어떨까요, 완벽한, 자신감에 가득 찬

            올바른 예시:
            노래 추천 요청 → https://open.spotify.com/track/3HAkoNmThZhyFejhpRXXYI?si=cbf278cca9e24ffb,https://open.spotify.com/track/3jsYQw78lrxJA2ysnmOIf9
            감정스코어 → 70/100
            감정코드 → CM
            MBTI 위로 → MBTI 있음: 'ENFP라서 새로운 사람들과의 만남이 정말 즐거웠을 것 같아요' / MBTI 없음: '오늘 하루도 정말 수고 많으셨어요'
            조언 요청 → '이런 감정을 느끼는 것은 자연스러운 일이에요. 천천히 자신의 감정을 받아들이고, 작은 변화부터 시도해보세요'
            해시태그 요청 → #싸움 #화남 #흐린날씨 #커피 #산책 #감사함

            잘못된 예시:
            '기쁨 감정이므로 JP코드를 추천드릴게요'
            '70/100! 완벽한 발표였나봐요'
            '일기 내용의 주요 키워드를 해시태그로 정리해드리면 #싸움 #화남...'

            JSON 형식 외의 다른 텍스트는 절대 포함하지 마세요."""
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
- 인사말, 질문, 마무리 인사, 조언, 위로, 공감 금지
- 오직 요약만 둥글둥글하게 작성
- 비속어나 부적절한 표현 절대 금지

예시:
일기: "오늘 회사에서 중요한 프레젠테이션을 했는데 팀장님이 칭찬해주셔서 정말 기뻤어요. 동료들과 회식도 하고 즐거운 하루였습니다."
응답: "회사에서 중요한 프레젠테이션을 진행하고 팀장님께 좋은 평가를 받았네요. 이후 동료들과 함께 회식 시간을 가지며 즐겁게 하루를 마무리했습니다."""

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