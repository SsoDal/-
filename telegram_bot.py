def format_to_html(report_text: str, mode: str) -> str:
    """
    JSON을 안정적으로 파싱하여 텔레그램용 HTML로 변환합니다.
    데이터 누락이나 특수문자로 인한 HTML 깨짐을 방지합니다.
    """
    cleaned = clean_json_text(report_text)
    
    try:
        data = json.loads(cleaned)
    except Exception as e:
        # 파싱 실패 시 상단 코드처럼 안전하게 원문 일부 반환
        print(f"JSON 파싱 실패: {e}")
        return f"<b>📊 {mode.upper()} 리포트 (원문)</b>\n\n{report_text[:900]}..."

    # 리포트 제목 설정
    report_title = data.get('report_title', f'{mode.upper()} 경제 리포트')
    html = f"<b>📊 {report_title}</b>\n\n"

    # 시장별 데이터 처리 (KOSPI, KOSDAQ)
    # 상단 코드의 안정적인 루프 구조와 하단 코드의 확장 필드 결합
    markets = [("kospi", "🔥", "코스피 TOP"), ("kosdaq", "🚀", "코스닥 TOP")]
    
    for key, emoji, title in markets:
        items = data.get(key, [])
        if not items:
            continue
            
        html += f"<b>{emoji} {title}</b>\n\n"
        
        # 최대 10개까지 처리하되 데이터가 있는 만큼만 반복
        for item in items[:10]:
            name = item.get('종목명', 'N/A')
            leader = item.get('대장주', 'N/A')
            sub_stock = item.get('차등주', 'N/A')
            
            # 종목 상단 라인 (대장주/차등주 정보 포함)
            html += f"📌 <b>{name}</b> (대장주: {leader} / 차등주: {sub_stock})\n"
            
            # 확률 및 신뢰도
            prob = item.get('상승확률', 0)
            conf = item.get('신뢰도', 0)
            html += f"   📈 상승확률 <b>{prob}%</b> | 📊 신뢰도 <b>{conf}%</b>\n"
            
            # 상세 내용 (항목별 안전하게 가져오기)
            reason = item.get('상승요인', '분석 중')
            target = item.get('목표가', '미정')
            source = item.get('출처', '기타')
            news = item.get('뉴스', '관련 뉴스 없음')
            
            html += f"   📋 요인: {reason}\n"
            html += f"   🎯 목표: {target}\n"
            html += f"   📍 출처: {source}\n"
            html += f"   📰 뉴스: {news}\n\n"

    html += "<i>⚠️ Gemini AI 분석 결과입니다. 투자 판단은 본인 책임입니다.</i>"
    return html
