from crawler import get_korean_news, get_us_news
from summarizer import compress_news
from ai_analyst import analyze_with_gemini
from telegram_bot import format_to_html, send_telegram, send_error_telegram
import sys
import traceback

def main():
    print("🚀 경제 비서 시스템 시작")
    
    try:
        # 1. 뉴스 수집
        print("📡 뉴스 크롤링 중...")
        korean_news = get_korean_news()
        us_news = get_us_news()
        print(f"   한국 뉴스 {len(korean_news)}개, 미국 뉴스 {len(us_news)}개 수집 완료")
        
        if not korean_news and not us_news:
            raise Exception("뉴스 수집 실패: 크롤링 결과가 없습니다.")
        
        # 2. 뉴스 압축
        compressed = compress_news(korean_news, us_news)
        
        # 3. AI 분석
        print("🤖 Gemini 분석 중...")
        recommendation = analyze_with_gemini(compressed)
        
        # 4. 텔레그램 전송
        html_msg = format_to_html(recommendation)
        send_telegram(html_msg)
        
        print("🎉 모든 작업 성공적으로 완료!")
        
    except Exception as e:
        # 상세 에러 정보 생성
        error_type = type(e).__name__
        error_message = str(e)
        error_trace = traceback.format_exc()
        
        error_summary = f"""❌ 경제 비서 시스템 실행 실패

🛠 에러 종류: {error_type}
📝 에러 메시지: {error_message}

📍 상세 스택 트레이스:
{error_trace[:800]}..."""   # 너무 길면 잘림 방지
        
        print(f"❌ 오류 발생: {error_type} - {error_message}")
        
        # 실패 알림을 텔레그램으로 전송
        try:
            send_error_telegram(error_summary)
            print("⚠️ 실패 알림을 텔레그램으로 전송했습니다.")
        except Exception as notify_error:
            print(f"🚨 실패 알림 전송마저 실패: {notify_error}")
        
        sys.exit(1)

if __name__ == "__main__":
    main()