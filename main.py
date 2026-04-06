import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime
import pytz

# 초기 설정
KST = pytz.timezone('Asia/Seoul')
now = datetime.now(KST)

def send_telegram(message):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    return requests.post(url, json=payload)

def get_kr_news():
    url = "https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1=101"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        titles = [t.get_text().strip() for t in soup.select('.list_body ul li dt:not(.photo) a')[:10]]
        return titles if titles else ["한국 뉴스를 가져오지 못했습니다."]
    except: return ["한국 뉴스 수집 중 연결 오류 발생"]

def get_us_news():
    url = "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US&ceid=US:en"
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.content, 'xml')
        items = soup.find_all('item')
        return [i.title.get_text() for i in items[:10]]
    except: return ["미국 뉴스 수집 중 연결 오류 발생"]

def main():
    try:
        # 1. 뉴스 수집
        kr_news = get_kr_news()
        us_news = get_us_news()
        
        # 2. AI 분석 설정
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        # 가장 범용적이고 에러 없는 모델명 사용
        model = genai.GenerativeModel('gemini-1.5-flash') 
        
        prompt = f"""
        당신은 수석 애널리스트입니다. 아래 뉴스를 보고 보고서를 작성하세요.
        HTML 태그(<b>, <i>)를 적절히 섞어 가독성 있게 작성하세요.
        
        1. 시장 요약: 한/미 뉴스 핵심 요약 (번역 포함)
        2. KOSPI 추천 5개: [종목명 / 목표치 / 적중확률 / 사유]
        3. KOSDAQ 추천 5개: [종목명 / 목표치 / 적중확률 / 사유]
        
        데이터:
        한국뉴스: {kr_news}
        미국뉴스: {us_news}
        """
        
        response = model.generate_content(prompt)
        report = response.text
        
        # 3. 전송
        final_msg = f"<b>[글로벌 증권 리포트 - {now.strftime('%H:%M')}]</b>\n\n{report}"
        send_telegram(final_msg)
        
    except Exception as e:
        # 에러 발생 시 텔레그램으로 에러 내용 즉시 보고
        send_telegram(f"⚠️ <b>시스템 에러 발생</b>\n원인: {str(e)}")

if __name__ == "__main__":
    main()
