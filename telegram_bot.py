import requests
import json
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from typing import Dict, Any

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
    """JSON을 예쁜 HTML + 이모티콘으로 변환"""
    try:
        data: Dict[str, Any] = json.loads(report_text)
    except:
        # JSON 파싱 실패 시 원문 그대로 전송
        return f"<b>📊 {mode.upper()} 리포트</b>\n\n{report_text}"

    html = f"<b>📊 {data.get('title', '오늘의 AI 종목 추천')}</b>\n\n"

    # 코스피
    html += "🔥 <b>코스피 TOP</b>\n"
    for item in data.get("KOSPI", [])[:5]:
        html += f"• <b>{item.get('종목명', 'N/A')}</b>\n"
        html += f"   📌 이유: {item.get('추천_이유', '')}\n"
        html += f"   ⚠️ 리스크: {item.get('리스크', '')}\n\n"

    # 코스닥
    html += "🔥 <b>코스닥 TOP</b>\n"
    for item in data.get("KOSDAQ", [])[:5]:
        html += f"• <b>{item.get('종목명', 'N/A')}</b>\n"
        html += f"   📌 이유: {item.get('추천_이유', '')}\n"
        html += f"   ⚠️ 리스크: {item.get('리스크', '')}\n\n"

    html += "<i>⚠️ AI 분석 결과이며 투자 권유가 아닙니다. 항상 본인 판단으로 투자하세요.</i>"
    return html