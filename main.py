# main.py 전체 교체
from crawler import get_korean_news, get_us_news
from summarizer import compress_news
from ai_analyst import analyze_with_gemini
from telegram_bot import format_to_html, send_telegram, send_error_telegram
import sys
import traceback

def main():
    print("🚀 경제 비서 시스템 시작 - 안전 모드")
    
    try:
        # Secrets 확인 (초반 체크)
        from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, GEMINI_API_KEY
        if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
            raise Exception("TELEGRAM_TOKEN 또는 TELEGRAM_CHAT_ID가 설정되지 않았습니다. GitHub Secrets를 확인하세요.")
        if not GEMINI_API_KEY:
            raise Exception("GEMINI_API_KEY가 설정되지 않았습니다.")
        
        print("✅ Secrets 확인 완료")
        
        # 1. 뉴스 수집
        print("📡 뉴스 크롤링 중...")
        korean_news = get_korean_news()
        us_news = get_us_news()
        print(f"   한국 뉴스 {len(korean_news)}개, 미국 뉴스 {len(us_news)}개 수집")
        
        if len(korean_news) == 0 and len(us_news) == 0:
            raise Exception("뉴스 수집이 전혀 되지 않았습니다. (크롤러 문제 의심)")
        
        # 2. 압축
        compressed = compress_news(korean_news, us_news)
        
        # 3. AI 분석
        print("🤖 Gemini 2.5 Flash 분석 중...")
        recommendation = analyze_with_gemini(compressed)
        
        # 4. 전송
        html_msg = format_to_html(recommendation)
        send_telegram(html_msg)
        
        print("🎉 모든 작업 성공!")
        
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        full_trace = traceback.format_exc()
        
        error_summary = f"""❌ <b>경제 비서 시스템 실행 실패</b>

🛠 에러 종류: <b>{error_type}</b>
📝 메시지: {error_msg}

📍 발생 위치: main.py
🔍 상세 트레이스 (앞부분):
<pre>{full_trace[:1200]}</pre>

GitHub Actions 로그를 확인해주세요."""

        print(f"❌ 실행 실패: {error_type} - {error_msg}")
        
        try:
            send_error_telegram(error_summary)
            print("✅ 실패 알림을 텔레그램으로 전송했습니다.")
        except Exception as notify_e:
            print(f"🚨 알림 전송마저 실패: {notify_e}")
            print("   → Secrets 문제 또는 Telegram Token 오류일 가능성이 매우 높습니다.")
        
        sys.exit(1)

if __name__ == "__main__":
    main()