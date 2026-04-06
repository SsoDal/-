import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime
import pytz

KST = pytz.timezone('Asia/Seoul')
now = datetime.now(KST)

def send_telegram(message):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    # 마크다운보다 에러가 적은 HTML 모드 유지
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    return requests.post(url, json=payload)

def get_kr_news():
    url = "https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1=101"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        return [t.get_text().strip() for t in soup.select('.list_body ul li dt:not(.photo) a')[:10]]
    except: return []

def get_us_news():
    url = "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US&ceid=US:en"
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.content, 'xml')
        return [i.title.get_text() for i in soup.find_all('item')[:10]]
    except: return []

def main():
    try:
        kr_news = get_kr_news()
        us_news = get_us_news()
        
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        
        # [핵심 수정] 2026년 표준 모델명인 gemini-2.0-flash 시도
        # 만약 실패할 경우를 대비해 리스트 형태로 순차 시도합니다.
        model_names = ['gemini-2.0-flash', 'gemini-1.5-flash-latest', 'gemini-1.5-pro']
        response_text = ""
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                prompt = f"""
                당신은 20년 경력의 수석 애널리스트입니다. 아래 뉴스를 토대로 리포트를 작성하세요.
                반드시 <b>태그를 활용해 가독성을 높이세요.
                
                1. 시장 브리핑 (한/미 주요 이슈 요약 및 번역)
                2. KOSPI 추천 5개 (종목명/목표가/적중확률/사유)
                3. KOSDAQ 추천 5개 (종목명/목표가/적중확률/사유)
                
                데이터:
                한국: {kr_news}
                미국: {us_news}
                """
                response = model.generate_content(prompt)
                response_text = response.text
                break # 성공하면 루프 탈출
            except Exception as e:
                print(f"{model_name} 시도 실패: {e}")
                continue
        
        if not response_text:
            raise Exception("모든 AI 모델 호출에 실패했습니다.")

        final_msg = f"<b>📊 글로벌 증권 리포트 ({now.strftime('%Y-%m-%d %H:%M')})</b>\n\n{response_text}"
        send_telegram(final_msg)
        
    except Exception as e:
        send_telegram(f"⚠️ <b>최종 시스템 에러</b>\n원인: {str(e)}")

if __name__ == "__main__":
    main()
