"""
경제 비서 메인 실행 파일
GitHub Actions에서 실행되며, Gemini로 분석 후 텔레그램 전송.
"""
import sys
import os

print("=" * 50)
print("🚀 경제 비서 시스템 시작 v8")
print("=" * 50)

# ── 환경변수 체크 ──────────────────────────────────
required_envs = ["GEMINI_API_KEY", "TELEGRAM_TOKEN", "TELEGRAM_CHAT_ID"]
missing = [k for k in required_envs if not os.getenv(k)]
if missing:
    print(f"❌ 필수 환경변수 누락: {missing}")
    sys.exit(1)
print(f"✅ 환경변수 확인 완료")

# ── 모듈 import ────────────────────────────────────
try:
    from ai_analyst import analyze_with_gemini
    from telegram_bot import format_to_html, send_telegram, send_error_telegram
    print("✅ 모듈 import 성공")
except ImportError as e:
    print(f"❌ import 실패: {e}")
    sys.exit(1)

# ── 뉴스 수집 (실제 프로덕션에선 크롤러로 교체) ──
NEWS_TEXT = """
- 미국 연준, 기준금리 동결 결정 — 인플레이션 우려 지속
- 삼성전자, HBM4 메모리 2분기 양산 본격화 발표
- SK하이닉스, AI 서버향 수요 급증으로 1분기 실적 개선 전망
- 현대차·기아, 미국 IRA 전기차 보조금 수혜 기대
- 코스피 2650선 회복 시도, 외국인 순매수 전환
- 카카오, AI 플랫폼 신규 서비스 출시 발표
- 네이버, 하이퍼클로바X 기업용 패키지 계약 확대
- LG에너지솔루션, 북미 배터리 공장 증설 계획 공개
- 바이오 섹터, 식약처 임상 3상 승인 다수 발표로 강세
- 원/달러 환율 1370원대 안정화, 외환당국 개입 경계
- POSCO홀딩스, 리튬 가격 반등으로 2차전지 소재 수익 회복
- 한화에어로스페이스, 방산 수출 계약 확대 — 폴란드·루마니아
- JP모건, 한국 증시 비중 확대 권고 — 반도체·방산 주목
"""


def main():
    mode = os.getenv("MODE", "full")
    print(f"📌 실행 모드: {mode}")

    # ── Step 1: Gemini 분석 ──────────────────────────
    print("\n[Step 1] Gemini AI 분석 시작...")
    try:
        report_data = analyze_with_gemini(NEWS_TEXT)
        kospi_cnt  = len(report_data.get("kospi", []))
        kosdaq_cnt = len(report_data.get("kosdaq", []))
        print(f"✅ 분석 완료 — 코스피 {kospi_cnt}개, 코스닥 {kosdaq_cnt}개")
    except Exception as e:
        msg = f"Gemini 분석 실패: {e}"
        print(f"❌ {msg}")
        send_error_telegram(msg)
        sys.exit(1)

    # ── Step 2: 메시지 포맷팅 ───────────────────────
    print("\n[Step 2] 텔레그램 메시지 생성...")
    try:
        html_msg = format_to_html(report_data, mode)
        print(f"✅ 메시지 생성 완료 ({len(html_msg)}자)")
    except Exception as e:
        msg = f"메시지 포맷팅 실패: {e}"
        print(f"❌ {msg}")
        send_error_telegram(msg)
        sys.exit(1)

    # ── Step 3: 텔레그램 전송 ───────────────────────
    print("\n[Step 3] 텔레그램 전송...")
    success = send_telegram(html_msg)
    if success:
        print("\n✅ 전체 프로세스 완료!")
        sys.exit(0)
    else:
        print("\n❌ 텔레그램 전송 실패")
        sys.exit(1)


if __name__ == "__main__":
    main()
