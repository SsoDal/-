import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime
import pytz

# 1. 초기 설정
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
KST = pytz.timezone('Asia/Seoul')
now = datetime.now(KST)

def get_kr_news():
    """한국 경제 뉴스 톱헤드라인 수집"""
    url = "https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1=101"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        return [t.get_text().strip() for t in soup.select('.list_body ul li dt:not(.photo) a')[:12]]
    except: return []

def get_us_news():
    """미국 경제 뉴스 수집 (Google News US - Business)"""
    # 필터를 완화하여 수집률을 높임
    url = "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US&ceid=US:en"
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'xml')
        return [t.get_text() for t in soup.select('item title')[:12]]
    except: return []

def analyze_and_send(kr_news, us_news, mode):
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    news_context = f"[한국 주요 뉴스]\n{kr_news}\n\n[미국 주요 뉴스]\n{us_news}"
    
    prompt = f"""
    당신은 20년 경력의 대한민국 최고의 증권 전략가이자 수석 애널리스트입니다.
    다음 뉴스를 분석하여 [글로벌 뉴스 브리핑]과 [종목 추천 리포트]를 작성하세요.

    1. 뉴스 분석: 한/미 경제 상황을 종합하여 시장의 핵심 흐름을 3문장으로 요약하세요. (영문 뉴스는 한국어로 번역)
    2. 종목 추천 (KOSPI 5종목, KOSDAQ 5종목):
       - 오늘 수집된 뉴스와 가장 연관성이 높은 종목을 선정하세요.
       - 각 종목별로 [종목명 / 예상 목표치 / 적중 확률(%) / 추천 사유]를 반드시 포함하세요.
       - 적중 확률은 현재 뉴스 데이터와 과거 패턴을 분석한 기술적 수치로 제시하세요.
    
    형식:
    🚨 [글로벌 경제 & 증권 비서 보고]
    
    [핵심 시장 브리핑]
    - 내용 요약...
    
    📊 [KOSPI 추천 TOP 5]
    1. 종목명: (목표가: 00원 / 적중확률: 00%) - 사유: ...
    ...
    
    🚀 [KOSDAQ 추천 TOP 5]
    1. 종목명: (목표가: 00원 / 적중확률: 00%) - 사유: ...
    
    ※ 본 정보는 AI 분석 결과로 투자 참고용이며 최종 책임은 본인에게 있습니다.
    
    데이터: {news_context}
    """
    
    try:
        response = model.generate_content(prompt).text.strip()
        
        # 텔레그램 전송
        url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage"
        requests.post(url, json={
            "chat_id": os.getenv("TELEGRAM_CHAT_ID"), 
            "text": response,
            "parse_mode": "Markdown"
        })
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    kr = get_kr_news()
    us = get_us_news()
    
    # 분석 모드 실행 (테스트 성공했으므로 이제 매번 분석 보고서를 보냅니다)
    analyze_and_send(kr, us, "report")
