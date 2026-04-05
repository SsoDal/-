import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime
import pytz

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
KST = pytz.timezone('Asia/Seoul')
now = datetime.now(KST)

def get_news():
    url = "https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1=101"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    return [t.get_text().strip() for t in soup.select('.list_body ul li dt:not(.photo) a')[:15]]

def analyze_and_send(news_list, mode):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompts = {
        "breaking": f"다음 뉴스 중 시장에 즉각 영향을 줄 긴급 속보만 1줄 요약해. 없으면 'PASS': {news_list}",
        "hourly": f"현재 경제 상황 핵심 3가지를 요약 보고해: {news_list}",
        "daily": f"오늘의 경제 지표와 주요 이슈를 총망라한 전문 레포트를 작성해: {news_list}"
    }
    response = model.generate_content(prompts[mode]).text.strip()
    if "PASS" not in response:
        header = {"breaking": "🚨 [경제 속보]", "hourly": f"🔔 {now.hour}시 브리핑", "daily": "📊 야간 심층 레포트"}[mode]
        url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage"
        requests.post(url, json={"chat_id": os.getenv("TELEGRAM_CHAT_ID"), "text": f"{header}\n\n{response}"})

if __name__ == "__main__":
    news = get_news()
    
    # 1. 밤 9시 (심층 레포트 보고)
    if now.hour == 21 and 0 <= now.minute < 10:
        analyze_and_send(news, "daily")
        
    # 2. 오전 7시 ~ 오후 6시 사이 정시 (브리핑 보고)
    elif 7 <= now.hour <= 18 and 0 <= now.minute < 10:
        analyze_and_send(news, "hourly")
        
    # 3. 그 외 모든 시간 (24시간 실시간 속보 감시)
    else:
        analyze_and_send(news, "breaking")
