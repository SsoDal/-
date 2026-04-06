import os
import requests
import time
from bs4 import BeautifulSoup
from google import genai
from datetime import datetime
import pytz

KST = pytz.timezone('Asia/Seoul')
now = datetime.now(KST)

def send_telegram(message):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id, 
        "text": message, 
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    requests.post(url, json=payload)

def get_kr_news():
    url = "https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1=101"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        titles = [t.get_text().strip() for t in soup.select('.list_body ul li dt:not(.photo) a')[:10]]
        return titles if titles else ["한국 뉴스 수집 결과 없음"]
    except Exception as e: return [f"한국 뉴스 오류: {e}"]

def get_us_news():
    url = "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US&ceid=US:en"
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.content, 'xml')
        return [i.title.get_text() for i in soup.find_all('item')[:10]]
    except Exception as e: return [f"미국 뉴스 오류: {e}"]

def main():
    try:
        kr_news = get_kr_news()
        us_news = get_us_news()
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("API 키 설정 누락")
        
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        당신은 20년 경력의 대한민국 최고 수석 애널리스트입니다.
        다음 뉴스를 분석하여 리포트를 작성하세요. 가독성을 위해 <b>태그를 사용하세요.

        1. [글로벌 뉴스 브리핑]: 한/미 경제 핵심 요약 (번역 포함)
        2. [KOSPI 추천 TOP 5]: 종목명 / 목표가 / 적중확률(%) / 추천 사유
        3. [KOSDAQ 추천 TOP 5]: 종목명 / 목표가 / 적중확률(%) / 추천 사유

        한국뉴스: {kr_news}
        미국뉴스: {us_news}
        """
        
        report = ""
        max_retries = 3
        
        # 429 방어용 재시도 로직
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=prompt
                )
                report = response.text
                break  # 성공 시 루프 탈출
            except Exception as api_err:
                err_str = str(api_err)
                if '429' in err_str or 'RESOURCE_EXHAUSTED' in err_str:
                    if attempt < max_retries - 1:
                        time.sleep(20)  # 20초 대기 후 재시도
                        continue
                raise RuntimeError(f"구글 API 거부: {err_str}")

        final_msg = f"<b>📊 글로벌 증권 리포트 ({now.strftime('%H:%M')})</b>\n\n{report}"
        send_telegram(final_msg)

    except Exception as e:
        error_msg = f"⚠️ <b>시스템 에러 발생</b>\n<b>상세 원인:</b> {str(e)}"
        send_telegram(error_msg)

if __name__ == "__main__":
    main()
