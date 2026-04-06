from typing import List, Dict

def compress_news(korean: List[Dict], us: List[Dict]) -> str:
    """토큰 절약을 위한 뉴스 압축 (제목 + 요약만)"""
    lines = ["=== 오늘 주요 경제 뉴스 ==="]
    
    lines.append("\n[한국 경제]")
    for news in korean:
        lines.append(f"• {news['title']}\n  {news['summary']}")
    
    lines.append("\n[미국 경제]")
    for news in us:
        lines.append(f"• {news['title']}\n  {news['summary']}")
    
    return "\n".join(lines)