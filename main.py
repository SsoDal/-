from crawler import get_korean_news, get_us_news
from summarizer import compress_news
from ai_analyst import analyze_with_gemini
from telegram_bot import format_to_html, send_telegram
import sys

def main():
    print("🚀 경제 비서 시스템 시작 (GitHub Actions)")
    
    try:
        # 1. 뉴스 수집
        print("📡 뉴스 크롤링 중...")
        korean_news = get_korean_news()
        us_news = get_us_news()
        print(f"   한국 뉴스 {len(korean_news)}개, 미국 뉴스 {len(us_news)}개 수집")
        
        # 2. 압축
        compressed = compress_news(korean_news, us_news)
        
        # 3. AI 분석 (429 자동 재시도 포함)
        print("🤖 Gemini 2.5 Flash 분석 중...")
        recommendation = analyze_with_gemini(compressed)
        
        # 4. 전송
        html_msg = format_to_html(recommendation)
        send_telegram(html_msg)
        
        print("🎉 모든 작업 완료!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()