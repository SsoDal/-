import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime
import pytz

# 1. 환경 설정 및 시간대 정의
KST = pytz.timezone('Asia/Seoul')
now = datetime.now(KST)

def send_telegram(message):
    """텔레그램 메시지 전송 (HTML 모드)"""
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id, 
        "text": message, 
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    return requests.post(url, json=payload)

def get_kr_news():
    """네이버 경제 뉴스 수집 (헤더 강화로 차단 방지)"""
    url = "https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1=101"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        titles = [t.get_text().strip() for t in soup.select('.list_body ul li dt:not(.photo) a')[:12]]
        return titles if titles else ["한국 뉴스 목록을 찾을 수 없습니다."]
    except Exception as e:
        return [f"한국 뉴스 수집 실패: {str(e)}"]

def get_us_news():
    """구글 뉴스(미국 경제) RSS 수집"""
    url = "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US&ceid=US:en"
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.content, 'xml')
        items = soup.find_all('item')
        return [i.title.get_text() for i in items[:12]]
    except Exception as e:
        return [f"미국 뉴스 수집 실패: {str(e)}"]

def main():
    try:
        # 뉴스 데이터 수집
        kr_news = get_kr_news()
        us_news = get_us_news()
        
        # Gemini API 설정
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise Exception("GEMINI_API_KEY가 설정되지 않았습니다.")
        
        genai.configure(api_key=api_key)
        
        # 2026년 기준 가용 모델 리스트 (우선순위 순)
        model_names = ['gemini-2.0-flash', 'gemini-1.5-flash-latest', 'gemini-1.5-flash']
        
        response_text = ""
        used_model = ""

        # 모델 순차 시도 (404 에러 방지용)
        for name in model_names:
            try:
                model = genai.GenerativeModel(name)
                prompt = f"""
                당신은 20년 경력의 대한민국 최고 수석 애널리스트입니다. 
                다음 뉴스를 분석하여 투자 리포트를 작성하세요. 
                가독성을 위해 핵심 문구는 <b>태그를 사용하고, 줄바꿈을 적절히 하세요.

                1. [글로벌 뉴스 브리핑]: 한/미 경제 핵심 요약 (미국 뉴스는 한국어로 번역 및 영향 분석)
                2. [KOSPI 추천 종목 TOP 5]: 종목명 / 예상 목표가 / 적중확률(%) / 추천 사유
                3. [KOSDAQ 추천 종목 TOP 5]: 종목명 / 예상 목표가 / 적중확률(%) / 추천 사유

                데이터:
                한국뉴스: {kr_news}
                미국뉴스: {us_news}
                """
                response = model.generate_content(prompt)
                response_text = response.text
                used_model = name
                break 
            except Exception as e:
                print(f"{name} 모델 호출 실패: {e}")
                continue

        if not response_text:
            raise Exception("모든 AI 모델 호출에 실패했습니다.")

        # 최종 메시지 구성 (HTML 형식)
        final_msg = f"<b>📊 실시간 증권 리포트 ({now.strftime('%H:%M')})</b>\n"
        final_msg += f"<i>분석 엔진: {used_model}</i>\n\n"
        final_msg += response_text
        
        # 전송
        send_telegram(final_msg)
        print("리포트 전송 성공")

    except Exception as e:
        # 에러 발생 시 사용자에게 직접 보고 (디버깅용)
        error_msg = f"⚠️ <b>증권 비서 시스템 에러</b>\n<b>원인:</b> {str(e)}\n<b>시간:</b> {now.strftime('%Y-%m-%d %H:%M:%S')}"
        send_telegram(error_msg)
        print(f"에러 발생: {e}")

if __name__ == "__main__":
    main()
