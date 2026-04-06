from crawler import get_korean_news, get_us_news
from summarizer import compress_news
from ai_analyst import analyze_with_gemini
from telegram_bot import send_telegram, send_error_telegram   # format_to_html은 이제 사용 안 함
import sys
import traceback

def main():
    print("🚀 경제 비서 시스템 시작 - 안정 버전 (fallback + 에러 알림 강화)")

    try:
        # Secrets 체크
        from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, GEMINI_API_KEY
        if not all([TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, GEMINI_API_KEY]):
            raise Exception("GitHub Secrets 누락 (GEMINI_API_KEY, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID 확인)")

        print("✅ Secrets 확인 완료")

        # 1. 뉴스 수집
        print("📡 뉴스 크롤링 중...")
        korean_news = get_korean_news()
        us_news = get_us_news()
        print(f"   한국 {len(korean_news)}개 | 미국 {len(us_news)}개 수집")

        if len(korean_news) + len(us_news) == 0:
            raise Exception("뉴스 수집 실패")

        # 2. 압축
        compressed = compress_news(korean_news, us_news)

        # 3. AI 분석 (fallback 포함)
        print("🤖 Gemini 분석 시작...")
        recommendation_text = analyze_with_gemini(compressed)

        # 4. 텔레그램 전송 (AI가 만든 텍스트 그대로 + 헤더)
        final_msg = f"<b>📊 오늘의 AI 종목 추천 (경제 비서)</b>\n\n{recommendation_text}"
        send_telegram(final_msg)

        print("🎉 모든 작업 성공!")

    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        full_trace = traceback.format_exc()

        error_summary = f"""⚠️ <b>증권 비서 시스템 에러</b>
<b>원인:</b> {error_msg}
<b>에러 종류:</b> {error_type}
<b>시간:</b> {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔍 상세:
{full_trace[:1500]}"""

        print(f"❌ 실행 실패: {error_type} - {error_msg}")

        try:
            send_error_telegram(error_summary)
            print("✅ 실패 알림을 텔레그램으로 전송했습니다.")
        except Exception as notify_e:
            print(f"🚨 알림 전송 실패: {notify_e}")

        sys.exit(1)

if __name__ == "__main__":
    main()