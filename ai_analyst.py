from google import genai
from google.genai.types import GenerateContentConfig
from config import GEMINI_API_KEY, SYSTEM_PROMPT

client = genai.Client()

def analyze_with_gemini(compressed_news: str, mode: str = "full") -> str:
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY가 설정되지 않았습니다.")

    prompt = f"""{SYSTEM_PROMPT}

{compressed_news}

JSON을 처음부터 끝까지 완전하게 출력하라. 
절대 중간에 끊지 말고, kospi와 kosdaq을 각각 정확히 5개씩 채워서 완성하라."""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
                max_output_tokens=12000
            )
        )
        print("✅ Gemini 분석 성공")
        return response.text
    except Exception as e:
        print(f"❌ Gemini 호출 실패: {e}")
        raise e
