import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime
import pytz

# 1. AI 모델 설정 (2026년 최신 모델명 적용)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
KST = pytz.timezone('Asia/Seoul')
now = datetime.now(KST)

def get_news():
    url = "https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1=101"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        # 뉴스 제목 추출 로직 강화
        titles = []
        for t in soup.select('.list_body ul li dt:not(.photo) a'):
            title_text = t.get_text().strip()
            if title_text:
                titles.append(title_text)
        return titles[:15]
    except Exception as e:
        print(f"뉴스 수집 오류: {e}")
        return []

def analyze_and_send(news_list, mode):
    # 모델명을 2.0 버전으로 업데이트하여 404 에러 해결
    model = genai.GenerativeModel('gemini-2.0-flash') 
    
    prompts = {
        "breaking": f"당신은 긴급 경제 비서입니다. 다음 뉴스 중 시장에 즉각적인 파급력이 있는 초긴급 속보만 골라 1줄로 보고하세요. 보고할 내용이 없으면 반드시 'PASS'라고만 답하세요: {news_list}",
        "hourly": f"현재 경제 상황의 핵심 키워드 3가지를 분석하여 요약 보고하세요: {news_list}",
        "daily": f"오늘 하루의 주요 경제 지표와 뉴스를 종합하여 내일 시장 전망을 포함한 심층 레포트를 작성하세요: {news_list}"
    }
    
    try:
        response = model.generate_content(prompts[mode]).text.strip()
        
        if "PASS" not in response:
            header = {"breaking": "🚨 [실시간 경제 속보]", "hourly": f"🔔 {now.hour}시 정시 브리핑", "daily": "📊 야간 심층 경제 레포트"}[mode]
            message = f"{header}\n\n{response}"
            
            url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage"
            requests.post(url, json={"chat_id": os.getenv("TELEGRAM_CHAT_ID"), "text": message, "parse_mode": "Markdown"})
    except Exception as e:
        print(f"AI 분석 또는 전송 오류: {e}")

if __name__ == "__main__":
    news = get_news()
    
    # 테스트를 위해 '조건 무시'하고 무조건 브리핑 실행!
    analyze_and_send(news, "hourly") 
    
    # 확인 후에는 다시 원래 코드로 돌려놓으셔야 24시간 조용히 감시합니다.