from crawler import get_korean_news, get_us_news
from summarizer import compress_news
from ai_analyst import analyze_with_gemini
from telegram_bot import format_to_html, send_telegram, send_error_telegram
import sys
import traceback
from datetime import datetime
import pytz

def main():
    print("🚀 경제 비서 시스템 시작")

    try:
        from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, GEMINI_API_KEY
        if not all([TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, GEMINI_API_KEY]):
            raise Exception("GitHub Secrets 누락")

        kst = datetime.now(pytz.timezone('Asia/Seoul'))
        hour = kst.hour
        print(f"🕒 현재 KST: {kst.strftime('%H:%M')}")

        if 7 <= hour <= 18:
            mode = "breaking"
            print("📰 실시간 속보 모드 (30분 간격)")
        elif hour == 21:
            mode = "full"
            print("📊 오후 9시 종합 브리핑 모드")
        else:
            print("⏰ 보고 시간대가 아닙니다.")
            sys.exit(0)

        korean_news = get_korean_news()
        us_news = get_us_news()
        if len(korean_news) + len(us_news) == 0:
            raise Exception("뉴스 수집 실패")

        compressed = compress_news(korean_news, us_news)
        recommendation_text = analyze_with_gemini(compressed, mode)

        html_msg = format_to_html(recommendation_text, mode)
        send_telegram(html_msg)

        print(f"🎉 {mode.upper()} 리포트 전송 완료!")

    except Exception as e:
        error_summary = f"""⚠️ <b>증권 비서 시스템 에러</b>
<b>원인:</b> {str(e)}
<b>시간:</b> {datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')}"""
        print(f"❌ 실패: {e}")
        try:
            send_error_telegram(error_summary)
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    main()
