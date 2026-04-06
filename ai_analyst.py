from google import genai
from google.genai import types
import json
from tenacity import retry, stop_after_attempt, wait_exponential
import google.genai.errors as genai_errors
from config import MODEL_NAME, SYSTEM_PROMPT, RECOMMENDATION_SCHEMA
import traceback

client = genai.Client()

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=10, max=60),
    retry=retry_if_exception_type((genai_errors.ClientError, Exception)),
    reraise=True
)
def analyze_with_gemini(compressed_news: str) -> dict:
    """Gemini 분석 (Structured JSON)"""
    user_prompt = f"""{compressed_news}

위 뉴스를 바탕으로 코스피 5개, 코스닥 5개 종목을 추천해줘."""

    full_contents = [
        types.Content(role="user", parts=[types.Part.from_text(text=SYSTEM_PROMPT)]),
        types.Content(role="user", parts=[types.Part.from_text(text=user_prompt)])
    ]

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=full_contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_json_schema=RECOMMENDATION_SCHEMA,
            temperature=0.3,
            max_output_tokens=2048
        )
    )
    
    try:
        result = json.loads(response.text)
        return result
    except json.JSONDecodeError as e:
        print(f"JSON 파싱 실패: {response.text[:500]}")
        raise e