from google import genai
from google.genai.types import GenerateContentConfig
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import google.genai.errors as genai_errors
from config import GEMINI_API_KEY, SYSTEM_PROMPT

client = genai.Client()

@retry(
    stop=stop_after_attempt(6),                    # 최대 6번 시도
    wait=wait_exponential(multiplier=2, min=8, max=60),  # 8초 → 16초 → 32초... 최대 60초 대기
    retry=retry_if_exception_type((genai_errors.ClientError, Exception)),
    reraise=True
)
def analyze_with_gemini(compressed_news: str, mode: str = "full") -> str:
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY가 설정되지 않았습니다.")

    model_list = [
        "gemini-2.5-flash-lite",   # 가장 가벼운 모델 우선
        "gemini-2.5-flash",
        "gemini-1.5-flash"
    ]

    mode_instruction = (
        "실시간 한국·미국·세계 경제 뉴스 속보 요약과 급등 가능성이 높은 종목 추천"
        if mode == "breaking" else
        "오늘 하루 종합 브리핑 형식으로 뉴스 요약과 종목 추천"
    )

    last_error = None

    for model_name in model_list:
        try:
            print(f"🔄 모델 시도: {model_name} ({mode} 모드)")
            
            prompt = f"""{SYSTEM_PROMPT}

{compressed_news}

{mode_instruction}
JSON을 처음부터 끝까지 완전하게 출력하라. 절대 중간에 끊지 마라."""

            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.25,
                    max_output_tokens=10000
                )
            )
            
            print(f"✅ {model_name} 분석 성공")
            return response.text

        except Exception as e:
            last_error = e
            error_msg = str(e)
            print(f"❌ {model_name} 실패: {error_msg[:150]}...")
            
            # 503 에러인 경우 더 길게 대기
            if "503" in error_msg or "UNAVAILABLE" in error_msg:
                print("⏳ 503 과부하 감지 → 30초 대기 후 재시도")
                import time
                time.sleep(30)
            continue

    # 모든 모델 실패
    raise Exception(f"모든 모델 호출 실패. 마지막 에러: {last_error}")
