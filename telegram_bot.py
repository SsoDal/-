import requests
import json
import re
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def send_telegram(html_message: str):
    """
    메시지를 분석하여 4000자 단위로 분할 전송하되, 
    HTML 태그가 깨지지 않도록 '종목 단위(\n\n)'로 나누어 보냅니다.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    MAX_LENGTH = 4000

    # 메시지가 제한 범위 내라면 바로 전송
    if len(html_message) <= MAX_LENGTH:
        messages = [html_message]
    else:
        # 종목 구분자인 '\n\n'을 기준으로 메시지 분할
        parts = html_message.split('\n\n')
        messages = []
        current_chunk = ""

        for part in parts:
            # 현재 뭉치에 다음 파트를 합쳤을 때 제한을 넘는지 확인
            if len(current_chunk) + len(part) + 2 > MAX_LENGTH:
                messages.append(current_chunk.strip())
                current_chunk = part + "\n\n"
            else:
                current_chunk += part + "\n\n"
        
        if current_chunk:
            messages.append(current_chunk.strip())

    # 분할된 메시지들을 순차적으로 전송
    for msg in messages:
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        try:
            r = requests.post(url, json=payload, timeout=15)
            r.raise_for_status()
        except Exception as e:
            print(f"❌ 텔레그램 전송 실패: {e}")


def format_to_html(report_text: str, mode: str) -> str:
    """JSON 데이터를 텔레그램용 HTML로 정교하게 변환"""
    cleaned = clean_json_text(report_text)
    
    try:
        data = json.loads(cleaned)
    except Exception as e:
        print(f"⚠️ JSON 파싱 실패: {e}")
        return f"<b>📊 {mode.upper()} 리포트 (원문)</b>\n\n{report_text[:900]}..."

    report_title = data.get('report_title', f'{mode.upper()} 경제 리포트')
    html = f"<b>📊 {report_title}</b>\n\n"

    markets = [("kospi", "🔥", "코스피 TOP"), ("kosdaq", "🚀", "코스닥 TOP")]
    
    for key, emoji, title in markets:
        items = data.get(key, [])
        if not items: continue
            
        html += f"<b>{emoji} {title}</b>\n\n"
        
        for item in items[:10]:
            # 데이터 안전 추출 (에러 방지)
            name = item.get('종목명', 'N/A')
            leader = item.get('대장주', 'N/A')
            sub = item.get('차등주', 'N/A')
            prob = item.get('상승확률', 0)
            conf = item.get('신뢰도', 0)
            reason = item.get('상승요인', '분석 중')
            target = item.get('목표가', '미정')
            source = item.get('출처', '기타')
            news = item.get('뉴스', '관련 뉴스 없음')
            
            # 한 종목 블록 생성
            html += f"📌 <b>{name}</b> (대장주: {leader} / 차등주: {sub})\n"
            html += f"   📈 상승확률 <b>{prob}%</b> | 📊 신뢰도 <b>{conf}%</b>\n"
            html += f"   📋 요인: {reason}\n"
            html += f"   🎯 목표: {target}\n"
            html += f"   📍 출처: {source}\n"
            html += f"   📰 뉴스: {news}\n\n" # 종목 간 구분을 위해 \n\n 유지

    html += "<i>⚠️ Gemini AI 분석 결과입니다. 투자 판단은 본인 책임입니다.</i>"
    return html

def clean_json_text(text: str) -> str:
    """JSON 코드 블록 및 불필요한 공백 제거"""
    if not text: return "{}"
    text = text.strip()
    text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r'^```\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'```\s*$', '', text, flags=re.MULTILINE)
    return text.strip('` \n\t')
