"""
抓取国际军事新闻
来源: 百度新闻搜索 + 搜狗新闻
输出: data/military-news.json
"""

import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "military-news.json")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
}


def fetch_baidu_news(keyword: str, max_items: int = 20) -> list[dict]:
    """从百度新闻搜索获取军事新闻"""
    news_list = []
    seen_urls = set()
    
    try:
        url = f"https://news.baidu.com/ns?word={keyword}&pn=0&rn={max_items}&cl=2&ct=1&tn=news&ie=utf-8"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
        soup = BeautifulSoup(resp.text, "lxml")
        
        for item in soup.select("div.result"):
            a_tag = item.find("a")
            if not a_tag:
                continue
            href = a_tag.get("href", "")
            title = a_tag.get_text(strip=True)
            
            source_tag = item.find("p", class_="c-author")
            source = source_tag.get_text(strip=True) if source_tag else "百度新闻"
            
            abstract_tag = item.find("div", class_="c-summary")
            abstract = abstract_tag.get_text(strip=True) if abstract_tag else ""
            
            if title and len(title) > 5 and href not in seen_urls:
                seen_urls.add(href)
                news_list.append({
                    "title": title,
                    "url": href,
                    "summary": abstract[:200],
                    "source": source.split("\xa0")[0] if "\xa0" in source else source,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                })
        
    except Exception as e:
        print(f"百度新闻抓取失败: {e}")
    
    return news_list


def main():
    print("正在抓取国际军事新闻...")
    
    keywords = ["国际军事", "军事新闻", "国防军事", "military", "defense"]
    
    all_news = []
    seen_titles = set()
    
    for kw in keywords:
        print(f"  搜索: {kw}")
        news = fetch_baidu_news(kw, max_items=15)
        for n in news:
            if n["title"] not in seen_titles:
                seen_titles.add(n["title"])
                all_news.append(n)
        if len(all_news) >= 30:
            break
    
    all_news = all_news[:30]
    print(f"获取完成，共 {len(all_news)} 条新闻")
    
    output = {
        "source": "百度新闻",
        "description": "国际军事新闻最新动态",
        "language": "zh-CN",
        "scraped_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_count": len(all_news),
        "data": all_news,
    }
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"数据已保存到 {OUTPUT_FILE}")
    for n in all_news[:5]:
        print(f"  {n['title'][:50]}")


if __name__ == "__main__":
    main()
