import time
import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"
MAX_MSG_LEN = 4000   # 텔레그램 한도 4096, 여유 있게 4000
MAX_RETRIES = 3
RETRY_DELAY = 3


def _send_single(text: str, token: str, chat_id: str) -> None:
    """단일 텍스트 조각을 텔레그램에 전송. 실패 시 재시도."""
    url = TELEGRAM_API.format(token=token)
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "disable_notification": False,
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(url, json=payload, timeout=15)

            if resp.status_code == 429:
                # Too Many Requests: retry_after 존재하면 그 만큼 대기
                retry_after = resp.json().get("parameters", {}).get("retry_after", 5)
                print(f"  ⚠️ 텔레그램 Rate limit. {retry_after}초 대기...")
                time.sleep(retry_after)
                continue

            resp.raise_for_status()
            result = resp.json()
            if not result.get("ok"):
                raise RuntimeError(f"텔레그램 API 오류: {result}")

            return  # 성공

        except (requests.RequestException, RuntimeError) as e:
            print(f"  ❌ 텔레그램 전송 시도 {attempt} 실패: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                raise RuntimeError(f"텔레그램 {MAX_RETRIES}회 전송 실패: {e}") from e


def send_telegram(message: str, token: str = None, chat_id: str = None) -> bool:
    """
    메시지를 텔레그램으로 전송.
    4000자 초과 시 자동 분할 전송.
    성공: True, 실패: False
    """
    token = token or TELEGRAM_TOKEN
    chat_id = chat_id or TELEGRAM_CHAT_ID

    if not token:
        print("❌ TELEGRAM_TOKEN이 없습니다.")
        return False
    if not chat_id:
        print("❌ TELEGRAM_CHAT_ID가 없습니다.")
        return False

    # 메시지 분할 (줄 단위로 끊어서 HTML 태그 손상 방지)
    chunks = _split_message(message, MAX_MSG_LEN)
    total = len(chunks)
    print(f"  📨 텔레그램 전송: {total}개 파트, 총 {len(message)}자")

    try:
        for i, chunk in enumerate(chunks, 1):
            _send_single(chunk, token, chat_id)
            print(f"  ✅ 파트 {i}/{total} 전송 완료 ({len(chunk)}자)")
            if i < total:
                time.sleep(1)  # 연속 전송 시 rate limit 방지
        return True

    except RuntimeError as e:
        print(f"❌ 텔레그램 전송 최종 실패: {e}")
        return False


def send_error_telegram(error_msg: str, token: str = None, chat_id: str = None) -> bool:
    """에러 메시지 전송 (에러 전송 자체가 실패해도 프로그램 중단 안 함)."""
    safe_msg = str(error_msg)[:800]
    message = f"<b>⚠️ 경제 비서 오류 발생</b>\n\n<code>{safe_msg}</code>"
    try:
        return send_telegram(message, token, chat_id)
    except Exception as e:
        print(f"  ❌ 에러 텔레그램 전송도 실패: {e}")
        return False


def _split_message(text: str, max_len: int) -> list:
    """긴 메시지를 max_len 이하로 줄 단위 분할."""
    if len(text) <= max_len:
        return [text]

    chunks = []
    current = ""
    for line in text.splitlines(keepends=True):
        if len(current) + len(line) > max_len:
            if current:
                chunks.append(current)
            current = line
        else:
            current += line
    if current:
        chunks.append(current)
    return chunks


def format_to_html(data: dict, mode: str = "full") -> str:
    """
    Gemini가 반환한 dict를 HTML 텔레그램 메시지로 변환.
    data는 ai_analyst.py의 analyze_with_gemini()가 반환한 검증된 dict.
    """
    html = f"<b>📊 {data.get('report_title', '실시간 경제 속보 및 종목 추천')}</b>\n\n"

    # 뉴스 속보
    html += "<b>📰 실시간 경제 뉴스 속보</b>\n"
    html += f"{data.get('news_brief', '-')}\n\n"
    html += "────────────────────\n\n"

    # 종목 추천
    markets = [
        ("kospi",  "🔥", "코스피 추천"),
        ("kosdaq", "🚀", "코스닥 추천"),
    ]
    for market, emoji, title in markets:
        items = data.get(market, [])
        html += f"<b>{emoji} {title} ({len(items)}개)</b>\n\n"

        if not items:
            html += "  ⚠️ 추천 종목 없음\n\n"
            continue

        for item in items:
            종목명       = item.get("종목명", "N/A")
            대장주       = item.get("대장주", "N/A")
            차등주       = item.get("차등주", "N/A")
            상승확률     = item.get("상승확률", 0)
            하락확률     = item.get("하락확률", 0)
            급락확률     = item.get("급락확률", 0)
            유입확률     = item.get("외인기관유입확률", 0)
            상승요인     = item.get("상승요인", "-")
            목표가       = item.get("목표가", "미정")
            뉴스         = item.get("뉴스", "-")

            html += f"📌 <b>{종목명}</b>\n"
            html += f"   대장주: <b>{대장주}</b>  |  차등주: {차등주}\n"
            html += (
                f"   📈 상승 <b>{상승확률}%</b> | "
                f"📉 하락 <b>{하락확률}%</b> | "
                f"⚠️ 급락 <b>{급락확률}%</b>\n"
            )
            html += f"   📥 외인·기관 유입확률: <b>{유입확률}%</b>\n"
            html += f"   📋 상승요인: {상승요인}\n"
            html += f"   🎯 목표가: {목표가}\n"
            html += f"   📰 {뉴스}\n\n"

    html += "<i>⚠️ AI 분석입니다. 투자 판단은 본인 책임입니다.</i>"
    return html
