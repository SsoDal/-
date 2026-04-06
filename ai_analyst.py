from google import genai
from google.genai.types import GenerationConfig
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import json
from config import MODEL_NAME, SYSTEM_PROMPT, RECOMMENDATION_SCHEMA
import google.genai.errors as genai_errors  # 429 등 에러 처리

client = genai.Client()  # 환경변수 GEMINI_API_KEY 자동 인식

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=8, max=60),
    retry=retry_if_exception_type((genai_errors.ClientError, Exception)),
    reraise=True
)
def analyze_with_gemini(compressed_news: str) -> dict:
    """Gemini 2.5 Flash + Structured JSON + Exponential Backoff"""
    user_prompt = f"""{compressed_news}

위 뉴스를 바탕으로 코스피 5개, 코스닥 5개 종목을 추천해줘."""

    full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=full_prompt,
        config=GenerationConfig(
            response_mime_type="application/json",
            response_schema=RECOMMENDATION_SCHEMA,
            temperature=0.3,
            top_p=0.95,
            max_output_tokens=2048
        )
    )
    
    # JSON 파싱
    result = json.loads(response.text)
    return result