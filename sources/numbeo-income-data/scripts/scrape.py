"""
抓取 Numbeo 各国平均月净工资 (Average Monthly Net Salary After Tax)
数据来源: https://www.numbeo.com/cost-of-living/country_price_rankings?itemId=105
数据在页面 JS: data.addRows([['Country', value], ...])
输出: data/numbeo-income.json
"""

import json
import os
import re
import requests
from datetime import datetime

URL = "https://www.numbeo.com/cost-of-living/country_price_rankings?itemId=105&displayCurrency=USD"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "numbeo-income.json")


def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_data_addrows(html: str) -> list[dict]:
    """从页面 JS data.addRows([...]) 中提取国家+薪资数据"""
    # 匹配 data.addRows([ ... ]);
    match = re.search(
        r"data\.addRows\(\[(.*?)\]\s*\)\s*;",
        html,
        re.DOTALL,
    )
    if not match:
        raise Exception("找不到 data.addRows 数据块")

    rows_text = match.group(1)
    # 提取每行: ['Country', 1234.56]
    pattern = re.compile(r"\['([^']+)'\s*,\s*([\d.]+)\]")
    matches = pattern.findall(rows_text)

    countries = []
    for rank, (country, salary_str) in enumerate(matches, start=1):
        countries.append({
            "rank": rank,
            "country": country,
            "monthly_net_salary_usd": float(salary_str),
        })

    return countries


def main():
    print("正在抓取 Numbeo 数据...")
    html = fetch_html(URL)

    print("正在解析 data.addRows...")
    countries = parse_data_addrows(html)
    print(f"解析完成，共 {len(countries)} 个国家/地区")

    output = {
        "source": "Numbeo",
        "url": URL,
        "description": "Average Monthly Net Salary (After Tax) by Country",
        "unit": "USD",
        "scraped_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_count": len(countries),
        "data": countries,
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"数据已保存到 {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
