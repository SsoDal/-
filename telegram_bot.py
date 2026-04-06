import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from typing import Dict

def format_to_html(recommendation: Dict) -> str:
    """성공 시 예쁜 HTML 메시지"""
    html = "<b>📊 오늘의 AI 종목 추천 (경제 비서)</b>\n\n"
    
    html += "<b>🔥 코스피 TOP 5</b>\n"
    for item in recommendation.get("kospi", []):
        html += f"• <b>{item['name']}</b> ({item['ticker']})\n"
        html += f"   이유: {item['reason']}\n"
        html += f"   리스크: {item['risk']}\n\n"
    
    html += "<b>🔥 코스닥 TOP 5</b>\n"
    for item in recommendation.get("kosdaq", []):
        html += f"• <b>{item['name']}</b> ({item['ticker']})\n"
        html += f"   이유: {item['reason']}\n"
        html += f"   리스크: {item['risk']}\n\n"
    
    html += "<i>⚠️ 이는 AI 분석 결과이며 투자 권유가 아닙니다. 항상 본인 판단으로 투자하세요.</i>"
    return html


def send_telegram(html_message: str):
    """성공 메시지 전송"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": html_message,
        "parse_mode": "HTML"
    }
    resp = requests.post(url, json=payload, timeout=15)
    resp.raise_for_status()
    print("✅ 성공 메시지 텔레그램 전송 완료")


def send_error_telegram(error_message: str):
    """실패 시 에러 상세 메시지 전송 (평문)"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": error_message,
        "parse_mode": "HTML"   # HTML 태그가 포함되어 있으므로 유지
    }
    resp = requests.post(url, json=payload, timeout=15)
    resp.raise_for_status()
    print("⚠️ 에러 알림 텔레그램 전송 완료")