import json
import time
import requests
from config import GEMINI_API_KEY, GEMINI_API_URL, SYSTEM_PROMPT

# Gemini 호출 설정
MAX_RETRIES = 3
RETRY_DELAY = 5  # 초
MAX_OUTPUT_TOKENS = 8192


def _call_gemini(prompt: str) -> str:
    """Gemini REST API 직접 호출. 실패 시 MAX_RETRIES번 재시도."""
    url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": MAX_OUTPUT_TOKENS,
            "responseMimeType": "application/json"
        }
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"  🔄 Gemini 호출 시도 {attempt}/{MAX_RETRIES}...")
            resp = requests.post(url, json=payload, timeout=90)

            if resp.status_code == 429:
                wait = RETRY_DELAY * attempt
                print(f"  ⚠️ Rate limit(429). {wait}초 대기 후 재시도...")
                time.sleep(wait)
                continue

            if resp.status_code == 503:
                wait = RETRY_DELAY * attempt
                print(f"  ⚠️ 서버 과부하(503). {wait}초 대기 후 재시도...")
                time.sleep(wait)
                continue

            resp.raise_for_status()
            data = resp.json()

            # 응답 파싱
            candidates = data.get("candidates", [])
            if not candidates:
                raise ValueError("Gemini 응답에 candidates가 없습니다.")

            finish_reason = candidates[0].get("finishReason", "")
            if finish_reason not in ("STOP", "MAX_TOKENS", ""):
                raise ValueError(f"Gemini 비정상 종료: finishReason={finish_reason}")

            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                raise ValueError("Gemini 응답 parts가 비어 있습니다.")

            text = parts[0].get("text", "").strip()
            if not text:
                raise ValueError("Gemini 응답 텍스트가 비어 있습니다.")

            # 응답 길이 체크 (너무 짧으면 잘린 것)
            if len(text) < 500:
                raise ValueError(f"Gemini 응답이 너무 짧습니다({len(text)}자). 잘렸을 가능성.")

            print(f"  ✅ Gemini 응답 수신 ({len(text)}자)")
            return text

        except (requests.RequestException, ValueError) as e:
            print(f"  ❌ 시도 {attempt} 실패: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                raise RuntimeError(f"Gemini {MAX_RETRIES}회 모두 실패: {e}") from e


def _validate_and_fix_json(text: str) -> dict:
    """JSON 파싱 + 필수 필드 검증 + 자동 보정."""
    # 혹시 마크다운 코드블록이 있으면 제거
    import re
    text = re.sub(r'^```(?:json)?\s*', '', text.strip())
    text = re.sub(r'\s*```$', '', text)
    text = text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 파싱 실패: {e}\n원문 앞부분: {text[:300]}")

    # 필수 키 확인
    for key in ("news_brief", "kospi", "kosdaq"):
        if key not in data:
            raise ValueError(f"필수 키 누락: '{key}'")

    # 종목 개수 확인 및 경고
    for market in ("kospi", "kosdaq"):
        count = len(data.get(market, []))
        if count == 0:
            raise ValueError(f"{market} 종목이 0개입니다. 응답이 잘린 것으로 판단.")
        if count < 5:
            print(f"  ⚠️ {market} 종목 수 부족: {count}개 (5개 요청)")

    # 확률 합계 보정 (100이 아닌 경우 자동 조정)
    for market in ("kospi", "kosdaq"):
        for item in data.get(market, []):
            up = int(item.get("상승확률", 70))
            dn = int(item.get("하락확률", 20))
            cr = int(item.get("급락확률", 10))
            total = up + dn + cr
            if total != 100:
                # 급락확률 조정으로 맞춤
                item["급락확률"] = max(0, cr + (100 - total))
            # 정수 보장
            item["상승확률"] = up
            item["하락확률"] = dn
            item["급락확률"] = item.get("급락확률", cr)
            item["외인기관유입확률"] = int(item.get("외인기관유입확률", 60))

    return data


def analyze_with_gemini(news_text: str) -> dict:
    """뉴스를 받아 Gemini 분석 후 검증된 dict 반환."""
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"[오늘의 뉴스 제목 목록]\n{news_text}\n\n"
        "위 뉴스를 기반으로 JSON을 처음부터 끝까지 완전하게 출력하라. "
        "kospi 5개, kosdaq 5개를 반드시 채워서 완성하라."
    )

    raw_text = _call_gemini(prompt)
    data = _validate_and_fix_json(raw_text)
    return data
