import google.generativeai as genai
from config import GEMINI_API_KEY, SYSTEM_PROMPT

def analyze_with_gemini(compressed_news: str) -> str:
    """구식 SDK + 모델 fallback (당신이 성공적으로 에러 메시지 받았던 방식)"""
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY가 설정되지 않았습니다.")

    genai.configure(api_key=GEMINI_API_KEY)

    # 2026년 4월 기준 안정적인 모델 순서 (2.0은 이미 종료됨)
    model_names = [
        'gemini-2.5-flash',
        'gemini-2.5-flash-lite',
        'gemini-1.5-flash'
    ]

    for name in model_names:
        try:
            print(f"🔄 모델 시도 중: {name}")
            model = genai.GenerativeModel(name)

            prompt = f"""{SYSTEM_PROMPT}

{compressed_news}

위 뉴스를 바탕으로 투자 리포트를 작성하세요.
가독성을 위해 <b>태그, <i>태그 등을 적절히 사용하고, 줄바꿈을 잘 넣어주세요."""

            response = model.generate_content(prompt)
            print(f"✅ {name} 모델 성공")
            return response.text

        except Exception as e:
            print(f"❌ {name} 모델 호출 실패: {e}")
            continue

    # 모든 모델 실패
    raise Exception("모든 AI 모델 호출에 실패했습니다.")