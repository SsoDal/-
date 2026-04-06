from google import genai
from google.genai.types import GenerateContentConfig
import json
from config import GEMINI_API_KEY, SYSTEM_PROMPT

client = genai.Client()  # GEMINI_API_KEY 자동 사용

def analyze_with_gemini(compressed_news: str, mode: str = "full") -> str:
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY가 설정되지 않았습니다.")

    mode_instruction = (
        "매우 짧고 빠른 속보 형식으로 코스피/코스닥 각각 정확히 7개 종목 추천"
        if mode == "breaking" else
        "상세 종합 브리핑 형식으로 코스피/코스닥 각각 정확히 7개 종목 추천"
    )

    prompt = f"""{SYSTEM_PROMPT}

{compressed_news}

{mode_instruction}
JSON을 처음부터 끝까지 완전하게 출력하라. 절대 중간에 끊지 마라."""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.3,
                max_output_tokens=8192
            )
        )
        print("✅ Gemini 분석 성공")
        return response.text
    except Exception as e:
        print(f"❌ Gemini 호출 실패: {e}")
        raise e
