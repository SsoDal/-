import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def format_to_html(recommendation: dict) -> str:
    html = "<b>📊 오늘의 AI 종목 추천</b>\n\n"
    html += "<b>🔥 코스피 TOP 5</b>\n"
    for item in recommendation.get("kospi", []):
        html += f"• <b>{item.get('name', 'N/A')}</b> ({item.get('ticker', 'N/A')})\n"
        html += f"   이유: {item.get('reason', '')}\n"
        html += f"   리스크: {item.get('risk', '')}\n\n"
    
    html += "<b>🔥 코스닥 TOP 5</b>\n"
    for item in recommendation.get("kosdaq", []):
        html += f"• <b>{item.get('name', 'N/A')}</b> ({item.get('ticker', 'N/A')})\n"
        html += f"   이유: {item.get('reason', '')}\n"
        html += f"   리스크: {item.get('risk', '')}\n\n"
    
    html += "<i>⚠️ AI 분석 결과입니다. 투자 판단은 본인 책임입니다.</i>"
    return html

def send_telegram(html_message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": html_message, "parse_mode": "HTML"}
    r = requests.post(url, json=payload, timeout=15)
    r.raise_for_status()

def send_error_telegram(error_message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": error_message, "parse_mode": "HTML"}
    r = requests.post(url, json=payload, timeout=15)
    r.raise_for_status()