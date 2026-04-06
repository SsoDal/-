import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from typing import List, Dict

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
}

def get_korean_news() -> List[Dict]:
    """네이버 경제 뉴스 검색 (최신 8개)"""
    url = "https://search.naver.com/search.naver?where=news&query=%EA%B2%BD%EC%A0%9C&sm=tab_opt&sort=0"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    
    soup = BeautifulSoup(resp.text, "html.parser")
    articles = []
    
    # 2026년 기준 안정적인 셀렉터 (필요 시 조정)
    for item in soup.select(".list_news .bx")[:8]:
        title_tag = item.select_one(".news_tit")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        link = title_tag["href"]
        desc = item.select_one(".news_dsc").get_text(strip=True) if item.select_one(".news_dsc") else ""
        
        articles.append({
            "source": "네이버 경제",
            "title": title,
            "link": link,
            "summary": desc[:150] + "..." if len(desc) > 150 else desc
        })
    return articles

def get_us_news() -> List[Dict]:
    """미국 비즈니스 뉴스 RSS (NYT Business)"""
    rss_url = "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml"
    resp = requests.get(rss_url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    
    root = ET.fromstring(resp.content)
    articles = []
    
    for item in root.findall(".//item")[:6]:
        title = item.find("title").text or ""
        link = item.find("link").text or ""
        description = item.find("description").text or ""
        
        articles.append({
            "source": "NYT Business",
            "title": title,
            "link": link,
            "summary": description[:150] + "..." if len(description) > 150 else description
        })
    return articles