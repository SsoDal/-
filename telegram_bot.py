import requests
import json
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def send_telegram(html_message: str):
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
    send_telegram(error_message)

def format_to_html(report_text: str, mode: str) -> str:
    """JSON 파싱 후 예쁜 HTML + 이모티콘 + 표 형식으로 변환"""
    try:
        data = json.loads(report_text)
    except:
        return f"<b>📊 {mode.upper()} 리포트</b>\n\n{report_text[:800]}..."

    html = f"<b>📊 {data.get('report_title', f'{mode.upper()} 경제 리포트')}</b>\n\n"

    for market, title in [("kospi", "🔥 코스피 TOP 7"), ("kosdaq", "🔥 코스닥 TOP 7")]:
        html += f"<b>{title}</b>\n"
        for item in data.get(market, [])[:7]:
            html += f"• <b>{item.get('종목명', 'N/A')}</b> "
            html += f"(상승확률 <b>{item.get('상승확률', 0)}%</b> | 신뢰도 <b>{item.get('신뢰도', 0)}%</b>)\n"
            html += f"   📌 상승요인: {item.get('상승요인', '')}\n"
            html += f"   🎯 목표가: {item.get('목표가', '미정')}\n"
            html += f"   📍 출처: {item.get('출처', '')}\n\n"

    html += "<i>⚠️ Gemini 분석 결과입니다. 투자 판단은 본인 책임입니다.</i>\n"
    html += "<i>※ Grok/ChatGPT/Claude/Perplexity 분석은 추가 API 필요</i>"
    return html
