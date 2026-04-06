import sys
import traceback

# 가장 먼저 import 해서 초반 에러 잡기
try:
    from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, GEMINI_API_KEY, MODEL_NAME
    from crawler import get_korean_news, get_us_news
    from summarizer import compress_news
    from ai_analyst import analyze_with_gemini
    from telegram_bot import send_error_telegram
except Exception as import_err:
    print(f"❌ 초기 import 실패: {import_err}")
    sys.exit(1)

def main():
    print("🚀 경제 비서 시스템 시작 - 안전 모드 v3 (11초 실패 대응)")

    try:
        if not all([TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, GEMINI_API_KEY]):
            raise Exception("GitHub Secrets 중 하나 이상이 비어 있습니다. (GEMINI_API_KEY, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID 확인)")

        print("✅ Secrets 확인 완료")

        # 1. 뉴스 크롤링 (타임아웃 강화)
        print("📡 뉴스 크롤링 중...")
        korean_news = get_korean_news()
        us_news = get_us_news()
        print(f"   한국 {len(korean_news)}개 | 미국 {len(us_news)}개 수집")

        if len(korean_news) + len(us_news) == 0:
            raise Exception("뉴스 수집 실패 - 크롤링 결과가 0개입니다.")

        # 2. 압축
        compressed = compress_news(korean_news, us_news)

        # 3. AI 분석
        print("🤖 Gemini 분석 시작...")
        recommendation = analyze_with_gemini(compressed)

        # 성공 전송
        from telegram_bot import format_to_html, send_telegram
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

⏱️ 실패 시점: 약 11초 경과

🔍 상세 트레이스:
<pre>{full_trace[:1800]}</pre>"""

        print(f"❌ 실패: {error_type} - {error_msg}")

        try:
            send_error_telegram(error_summary)
            print("✅ 실패 알림을 텔레그램으로 전송했습니다.")
        except Exception as notify_e:
            print(f"🚨 알림 전송 실패: {notify_e} → Telegram Secrets 문제일 가능성 높음")

        sys.exit(1)

if __name__ == "__main__":
    main()