import requests
import json
import re
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def send_telegram(html_message: str):
    """텔레그램으로 HTML 메시지 전송"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": html_message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    r = requests.post(url, json=payload, timeout=15)
    r.raise_for_status()

def send_error_telegram(error_message: str):
    """에러 알림 전송"""
    try:
        send_telegram(error_message)
    except:
        pass

def clean_json_text(text: str) -> str:
    if not text:
        return "{}"
    text = text.strip()
    text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r'^```\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'```\s*$', '', text, flags=re.MULTILINE)
    return text.strip('` \n\t')

def format_to_html(report_text: str, mode: str) -> str:
    cleaned = clean_json_text(report_text)
    try:
        data = json.loads(cleaned)
    except:
        return f"<b>📊 {mode.upper()} 리포트</b>\n\n{report_text[:1500]}..."

    html = f"<b>📊 {data.get('report_title', f'{mode.upper()} 경제 리포트')}</b>\n\n"

    html += "<b>📰 실시간 경제 뉴스 속보</b>\n"
    html += f"{data.get('news_brief', '뉴스 속보를 불러오는 중...')}\n\n"
    html += "────────────────────\n\n"

    for market, emoji, title in [("kospi", "🔥", "코스피 추천"), ("kosdaq", "🚀", "코스닥 추천")]:
        html += f"<b>{emoji} {title}</b>\n\n"
        items = data.get(market, [])
        if not items:
            html += "   (현재 추천 종목이 없습니다)\n\n"
            continue
        for item in items[:8]:
            html += f"📌 <b>{item.get('종목명', 'N/A')}</b> "
            html += f"(대장주: <b>{item.get('대장주', 'N/A')}</b>, 차등주: {item.get('차등주', 'N/A')})\n"
            html += f"   📈 상승확률 <b>{item.get('상승확률', 0)}%</b>\n"
            html += f"   📋 상승요인: {item.get('상승요인', '')}\n"
            html += f"   🎯 목표가: {item.get('목표가', '미정')}\n"
            html += f"   📰 뉴스: {item.get('뉴스', '관련 뉴스 없음')}\n\n"

    html += "<i>⚠️ Gemini AI 분석 결과입니다. 투자 판단은 본인 책임입니다.</i>"
    return html
