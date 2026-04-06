from google import genai
from google.genai import types
import json
from tenacity import retry, stop_after_attempt, wait_exponential
import google.genai.errors as genai_errors
from config import MODEL_NAME, SYSTEM_PROMPT, RECOMMENDATION_SCHEMA

client = genai.Client()  # api_key는 환경변수에서 자동 로드

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=10, max=60),
    retry=retry_if_exception_type((genai_errors.ClientError, Exception)),
    reraise=True
)
def analyze_with_gemini(compressed_news: str) -> dict:
    user_prompt = f"""{compressed_news}

위 뉴스를 바탕으로 코스피 5개, 코스닥 5개 종목을 추천해줘. JSON 형식으로만 답변."""

    # 단순화된 호출 방식 (최신 SDK에 더 안전)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            SYSTEM_PROMPT,
            user_prompt
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_json_schema=RECOMMENDATION_SCHEMA,
            temperature=0.3,
            max_output_tokens=2048
        )
    )
    
    try:
        result = json.loads(response.text)
        if not isinstance(result, dict) or "kospi" not in result:
            raise ValueError("올바른 JSON 형식이 아님")
        return result
    except Exception as json_err:
        print(f"JSON 파싱 실패: {response.text[:300]}")
        raise json_err