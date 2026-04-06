import google.generativeai as genai
from config import GEMINI_API_KEY, SYSTEM_PROMPT

def analyze_with_gemini(compressed_news: str, mode: str = "full") -> str:
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY가 설정되지 않았습니다.")

    genai.configure(api_key=GEMINI_API_KEY)

    model_names = ['gemini-2.5-flash', 'gemini-2.5-flash-lite', 'gemini-1.5-flash']

    mode_instruction = (
        "실시간 한국·미국·세계 경제 뉴스 속보 요약과 함께 급등 가능성이 높은 종목을 추천"
        if mode == "breaking" else
        "오늘 하루 종합 브리핑 형식으로 뉴스 요약과 종목 추천"
    )

    for name in model_names:
        try:
            print(f"🔄 모델 시도: {name} ({mode} 모드)")
            model = genai.GenerativeModel(
                name,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.3,
                    max_output_tokens=8192
                )
            )

            prompt = f"""{SYSTEM_PROMPT}

{compressed_news}

{mode_instruction}
뉴스 속보 요약(news_brief)과 종목 추천을 함께 JSON에 포함시켜라.
JSON을 끝까지 완전하게 출력하라."""

            response = model.generate_content(prompt)
            print(f"✅ {name} 성공")
            return response.text

        except Exception as e:
            print(f"❌ {name} 실패: {e}")
            continue

    raise Exception("모든 AI 모델 호출에 실패했습니다.")
