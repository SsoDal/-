import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from typing import List, Dict

# 더 현실적인 브라우저 헤더 (2026년 기준)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0",
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Referer": "https://www.naver.com/"
}

def get_korean_news() -> List[Dict]:
    """네이버 경제 뉴스 (차단 회피 강화)"""
    urls = [
        "https://search.naver.com/search.naver?where=news&query=%EA%B2%BD%EC%A0%9C&sm=tab_opt&sort=0",
        "https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1=101"  # 대체 URL
    ]
    
    for url in urls:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                articles = []
                
                # 여러 가능한 셀렉터 시도
                items = soup.select(".news_contents") or soup.select(".bx") or soup.select("li.bx") or soup.select(".list_body ul li")
                
                for item in items[:10]:
                    title_tag = item.select_one("a.news_tit") or item.select_one(".news_tit a") or item.select_one("dt a")
                    if not title_tag:
                        continue
                    title = title_tag.get_text(strip=True)
                    link = title_tag.get("href", "")
                    desc = item.select_one(".news_dsc") or item.select_one(".dsc_txt")
                    summary = desc.get_text(strip=True)[:180] if desc else ""
                    
                    if title:
                        articles.append({
                            "source": "네이버 경제",
                            "title": title,
                            "link": link,
                            "summary": summary
                        })
                if articles:
                    return articles
        except Exception as e:
            print(f"Naver 크롤링 시도 실패 ({url}): {e}")
            continue
    
    print("⚠️ 모든 네이버 URL 차단됨 → 대체 뉴스 사용")
    return [{"source": "대체", "title": "네이버 경제 뉴스 접근 제한 중", "link": "", "summary": "실시간 경제 뉴스 수집이 일시적으로 제한되었습니다."}]

def get_us_news() -> List[Dict]:
    """미국 경제 뉴스 RSS (상대적으로 안정적)"""
    try:
        url = "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml"
        resp = requests.get(url, timeout=10, headers=HEADERS)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        articles = []
        for item in root.findall(".//item")[:8]:
            title = item.find("title").text or ""
            link = item.find("link").text or ""
            desc = item.find("description").text or "" if item.find("description") is not None else ""
            articles.append({
                "source": "NYT Business",
                "title": title,
                "link": link,
                "summary": desc[:180]
            })
        return articles
    except Exception as e:
        print(f"US 뉴스 RSS 실패: {e}")
        return [{"source": "대체", "title": "미국 경제 뉴스 수집 실패", "link": "", "summary": ""}]
