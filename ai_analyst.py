import google.generativeai as genai
from config import GEMINI_API_KEY, SYSTEM_PROMPT

def analyze_with_gemini(compressed_news: str, mode: str = "full") -> str:
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY가 설정되지 않았습니다.")

    genai.configure(api_key=GEMINI_API_KEY)

    model_names = ['gemini-2.5-flash', 'gemini-2.5-flash-lite', 'gemini-1.5-flash']

    mode_instruction = (
        "매우 짧고 빠른 속보 형식으로 코스피/코스닥 각 7개 종목 추천"
        if mode == "breaking" else
        "상세 종합 브리핑 형식으로 코스피/코스닥 각 7개 종목 추천"
    )

    for name in model_names:
        try:
            print(f"🔄 모델 시도: {name} ({mode} 모드)")
            model = genai.GenerativeModel(
                name,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.3,
                    max_output_tokens=4096
                )
            )

            prompt = f"""{SYSTEM_PROMPT}

{compressed_news}

{mode_instruction}
뉴스에 없는 내용은 절대 만들지 말고, JSON을 완전하게 끝까지 출력하라."""

            response = model.generate_content(prompt)
            print(f"✅ {name} 성공")
            return response.text

        except Exception as e:
            print(f"❌ {name} 실패: {e}")
            continue

    raise Exception("모든 AI 모델 호출에 실패했습니다.")
