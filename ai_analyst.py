from google import genai
import json
from tenacity import retry, stop_after_attempt, wait_exponential
import google.genai.errors as genai_errors
from config import MODEL_NAME, SYSTEM_PROMPT, RECOMMENDATION_SCHEMA

client = genai.Client()

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=8, max=45),
    retry=retry_if_exception_type((genai_errors.ClientError, Exception)),
    reraise=True
)
def analyze_with_gemini(compressed_news: str) -> dict:
    """최대한 단순화된 Gemini 호출 (2026년 최신 SDK 안전 방식)"""
    prompt = f"""{SYSTEM_PROMPT}

{compressed_news}

위 뉴스를 바탕으로 코스피 5개, 코스닥 5개 종목을 추천해줘. 반드시 JSON 형식으로만 답변해."""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,                    # ← 문자열로 단순 전달 (SDK가 자동 변환)
        config={
            "response_mime_type": "application/json",
            "response_json_schema": RECOMMENDATION_SCHEMA,
            "temperature": 0.3,
            "max_output_tokens": 2048
        }
    )
    
    try:
        result = json.loads(response.text)
        return result
    except Exception as e:
        print(f"JSON 파싱 실패: {response.text[:400] if hasattr(response, 'text') else 'No response'}")
        raise e