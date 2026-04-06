import requests
import json
import re
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
    try:
        send_telegram(error_message)
    except:
        pass

def clean_json_text(text: str) -> str:
    """JSON 깨짐 복구 - 더 강력하게"""
    if not text:
        return "{}"
    text = text.strip()
    
    # 코드블록 제거
    text = re.sub(r'^```json
    text = re.sub(r'^```\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'```\s*$', '', text, flags=re.MULTILINE)
    
    # 불필요한 앞뒤 문자 제거
    text = text.strip('` \n\t')
    
    return text

def format_to_html(report_text: str, mode: str) -> str:
    """JSON → 초깔끔 HTML (부호 전혀 안 보이게)"""
    cleaned = clean_json_text(report_text)
    
    try:
        data = json.loads(cleaned)
    except Exception as e:
        print(f"JSON 파싱 실패: {e}")
        return f"<b>📊 {mode.upper()} 리포트</b>\n\n{report_text[:800]}..."

    html = f"<b>📊 {data.get('report_title', f'{mode.upper()} 경제 리포트')}</b>\n\n"

    for market, emoji, title in [("kospi", "🔥", "코스피 TOP 7"), ("kosdaq", "🚀", "코스닥 TOP 7")]:
        html += f"<b>{emoji} {title}</b>\n\n"
        for item in data.get(market, [])[:7]:
            html += f"📌 <b>{item.get('종목명', 'N/A')}</b>\n"
            html += f"   📈 상승확률 <b>{item.get('상승확률', 0)}%</b> | "
            html += f"📊 신뢰도 <b>{item.get('신뢰도', 0)}%</b>\n"
            html += f"   📋 상승요인: {item.get('상승요인', '')}\n"
            html += f"   🎯 목표가: {item.get('목표가', '미정')}\n"
            html += f"   📍 출처: {item.get('출처', '')}\n\n"

    html += "<i>⚠️ Gemini AI 분석 결과입니다. 투자 판단은 본인 책임입니다.</i>"
    return html
