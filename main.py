import sys
import traceback
from datetime import datetime
import pytz

print("🚀 경제 비서 시스템 시작 - 안전 모드 v7 (최종 안정화)")

try:
    from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, GEMINI_API_KEY
    from crawler import get_korean_news, get_us_news
    from summarizer import compress_news
    from ai_analyst import analyze_with_gemini
    from telegram_bot import format_to_html, send_telegram, send_error_telegram   # send_telegram 명확히 import
    print("✅ 모든 모듈 import 성공")
except Exception as import_err:
    error_type = type(import_err).__name__
    error_msg = str(import_err)
    print(f"❌ 초기 import 실패: {error_type} - {error_msg}")
    traceback.print_exc()
    
    error_summary = f"""⚠️ <b>초기 Import 에러</b>
<b>에러 종류:</b> {error_type}
<b>메시지:</b> {error_msg}
<b>시간:</b> {datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')}"""
    try:
        send_error_telegram(error_summary)
    except:
        pass
    sys.exit(1)

def main():
    try:
        if not all([TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, GEMINI_API_KEY]):
            raise Exception("GitHub Secrets 누락")

        kst = datetime.now(pytz.timezone('Asia/Seoul'))
        hour = kst.hour
        print(f"🕒 현재 KST: {kst.strftime('%H:%M')}")

        mode = "full" if hour == 21 else "breaking"

        print("📡 뉴스 크롤링 중...")
        korean_news = get_korean_news()
        us_news = get_us_news()

        compressed = compress_news(korean_news, us_news)
        recommendation_text = analyze_with_gemini(compressed, mode)

        html_msg = format_to_html(recommendation_text, mode)
        send_telegram(html_msg)

        print(f"🎉 {mode.upper()} 리포트 전송 성공!")

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
