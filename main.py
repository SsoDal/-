import sys
import traceback
from datetime import datetime
import pytz

print("🚀 경제 비서 시스템 시작 - 안전 모드 v6")

try:
    from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, GEMINI_API_KEY
    from crawler import get_korean_news, get_us_news
    from summarizer import compress_news
    from ai_analyst import analyze_with_gemini
    from telegram_bot import format_to_html, send_telegram, send_error_telegram
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
            raise Exception("GitHub Secrets 중 하나 이상이 누락되었습니다.")

        print("✅ Secrets 확인 완료")

        kst = datetime.now(pytz.timezone('Asia/Seoul'))
        hour = kst.hour
        print(f"🕒 현재 KST: {kst.strftime('%H:%M')}")

        if hour == 21:
            mode = "full"
            print("📊 오후 9시 종합 브리핑 모드")
        else:
            mode = "breaking"
            print("📰 실시간 속보 + 급등주 모드 (24시간 운영)")

        print("📡 뉴스 크롤링 중...")
        korean_news = get_korean_news()
        us_news = get_us_news()
        print(f"   한국 {len(korean_news)}개 | 미국 {len(us_news)}개")

        if len(korean_news) + len(us_news) == 0:
            raise Exception("뉴스 수집 실패")

        compressed = compress_news(korean_news, us_news)
        print("📝 뉴스 압축 완료")

        print("🤖 Gemini 분석 시작...")
        recommendation_text = analyze_with_gemini(compressed, mode)

        html_msg = format_to_html(recommendation_text, mode)
        send_telegram(html_msg)

        print(f"🎉 {mode.upper()} 리포트 전송 성공!")

    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        full_trace = traceback.format_exc()

        error_summary = f"""⚠️ <b>증권 비서 시스템 에러</b>

<b>에러 종류:</b> {error_type}
<b>메시지:</b> {error_msg}
<b>시간:</b> {datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')}

🔍 상세 트레이스:
<pre>{full_trace[:2000]}</pre>"""

        print(f"❌ 실패: {error_type} - {error_msg}")
        traceback.print_exc()

        try:
            send_error_telegram(error_summary)
            print("✅ 에러 알림 전송 완료")
        except:
            pass

        sys.exit(1)

if __name__ == "__main__":
    main()
