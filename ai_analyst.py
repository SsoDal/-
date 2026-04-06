import google.generativeai as genai
from config import GEMINI_API_KEY, SYSTEM_PROMPT

def analyze_with_gemini(compressed_news: str, mode: str = "full") -> str:
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY가 설정되지 않았습니다.")

    genai.configure(api_key=GEMINI_API_KEY)

    model_names = ['gemini-2.5-flash', 'gemini-2.5-flash-lite', 'gemini-1.5-flash']

    mode_instruction = (
        "매우 짧고 빠른 속보 형식으로 코스피/코스닥 각각 정확히 7개 종목 추천"
        if mode == "breaking" else
        "상세 종합 브리핑 형식으로 코스피/코스닥 각각 정확히 7개 종목 추천"
    )

    for name in model_names:
        try:
            print(f"🔄 모델 시도: {name} ({mode} 모드)")
            model = genai.GenerativeModel(
                name,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.3,
                    max_output_tokens=8192,          # 대폭 증가
                    top_p=0.95
                )
            )

            prompt = f"""{SYSTEM_PROMPT}

{compressed_news}

{mode_instruction}
JSON을 처음부터 끝까지 완전하게 출력하라. 절대 중간에 끊지 마라. 
모든 배열은 정확히 7개 항목이어야 한다."""

            response = model.generate_content(prompt)
            print(f"✅ {name} 모델 성공")
            return response.text

        except Exception as e:
            print(f"❌ {name} 실패: {e}")
            continue

    raise Exception("모든 AI 모델 호출에 실패했습니다.")
