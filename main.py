import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime
import pytz

# 1. 설정
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
KST = pytz.timezone('Asia/Seoul')
now = datetime.now(KST)

def get_kr_news():
    """한국 경제 속보 수집"""
    url = "https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1=101"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        return [t.get_text().strip() for t in soup.select('.list_body ul li dt:not(.photo) a')[:10]]
    except: return []

def get_us_news():
    """미국 경제 속보 수집 (Google News US)"""
    # 구글 뉴스 미국 경제 섹션 RSS/HTML
    url = "https://news.google.com/rss/search?q=when:1h+allinurl:reuters.com+OR+allinurl:bloomberg.com&hl=en-US&gl=US&ceid=US:en"
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'xml')
        return [t.get_text() for t in soup.select('item title')[:10]]
    except: return []

def analyze_and_send(kr_news, us_news, mode):
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    combined_news = f" [한국 뉴스]\n{kr_news}\n\n[미국 뉴스(영문)]\n{us_news}"
    
    prompts = {
        "breaking": f"""당신은 글로벌 투자 전략가입니다. 다음 한/미 뉴스 중 한국 시장에 즉각 영향을 줄 '초긴급 속보'만 골라 요약하세요. 
        영어 뉴스는 반드시 한국어로 번역 및 요약하고, 해당 뉴스가 왜 중요한지 1문장 덧붙이세요.
        중요한 내용이 없으면 'PASS'라고만 답하세요.
        뉴스 데이터: {combined_news}""",
        
        "hourly": f"현재 한/미 양국의 주요 경제 상황 3가지를 요약하세요. 영어 뉴스는 한국어로 번역하세요: {combined_news}",
        
        "daily": f"오늘의 한/미 통합 경제 레포트를 작성하세요. 주요 지표와 글로벌 이슈를 분석하고 내일 증시 전망을 포함하세요: {combined_news}"
    }
    
    try:
        response = model.generate_content(prompts[mode]).text.strip()
        
        if "PASS" not in response:
            header = {"breaking": "🌐 [글로벌 긴급 속보]", "hourly": f"🔔 {now.hour}시 글로벌 브리핑", "daily": "📊 글로벌 심층 레포트"}[mode]
            message = f"{header}\n\n{response}"
            
            url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage"
            requests.post(url, json={"chat_id": os.getenv("TELEGRAM_CHAT_ID"), "text": message})
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    kr = get_kr_news()
    us = get_us_news()
    
    if not kr and not us: exit()

    # 시간별 실행 로직
    if now.hour == 21 and 0 <= now.minute < 10:
        analyze_and_send(kr, us, "daily")
    elif 7 <= now.hour <= 18 and 0 <= now.minute < 10:
        analyze_and_send(kr, us, "hourly")
    else:
        analyze_and_send(kr, us, "breaking")
