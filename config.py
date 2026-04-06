import os

# GitHub Secrets에서 불러옴
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 모델 설정 (2026년 기준 최신 추천)
MODEL_NAME = "gemini-2.5-flash"

# 시스템 프롬프트 (F&B 프랜차이즈 대표님 맞춤)
SYSTEM_PROMPT = """너는 15년차 한국 증권 애널리스트이자, 부산 기반 F&B 프랜차이즈 기업가의 개인 경제 비서다.
목표: 오늘 한국/미국 경제 뉴스에서 코스피/코스닥 종목 중 **단기(1\~4주) 상승 가능성이 높은 5개씩**을 정확하게 추천.
반드시 지켜야 할 규칙:
- 정치·매크로 뉴스보다는 '업종별 직접 수혜'가 명확한 종목만 추천
- 추천 이유는 구체적인 뉴스 사실 인용
- 과도한 낙관 금지, 반드시 리스크 1줄 언급
- 출력은 **반드시 아래 JSON 형식만** (마크다운, 설명, 추가 텍스트 절대 금지)"""

# JSON 스키마 (Gemini structured output용)
RECOMMENDATION_SCHEMA = {
    "type": "object",
    "properties": {
        "kospi": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string"},
                    "name": {"type": "string"},
                    "reason": {"type": "string"},
                    "risk": {"type": "string"}
                },
                "required": ["ticker", "name", "reason", "risk"]
            }
        },
        "kosdaq": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string"},
                    "name": {"type": "string"},
                    "reason": {"type": "string"},
                    "risk": {"type": "string"}
                },
                "required": ["ticker", "name", "reason", "risk"]
            }
        }
    },
    "required": ["kospi", "kosdaq"]
}