"""
抓取中概股最新数据
使用 yfinance 获取在美上市的中国公司股票数据
输出: data/china-adr-data.json
"""

import json
import os
import yfinance as yf
from datetime import datetime

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "china-adr-data.json")

# 主要中概股列表（美股 ADR）
CHINA_ADR_TICKERS = [
    # 电商/零售
    "BABA",   # 阿里巴巴
    "JD",     # 京东
    "PDD",    # 拼多多
    "VIPS",   # 唯品会
    "YUMC",   # 百胜中国
    "DADA",   # 达达
    # 搜索/内容/社交
    "BIDU",   # 百度
    "BILI",   # 哔哩哔哩
    "MOMO",   # 挚文集团（陌陌）
    "WB",     # 微博
    "DOYU",   # 斗鱼
    "HUYA",   # 虎牙
    # 教育
    "TAL",    # 好未来
    "EDU",    # 新东方
    "GOTU",   # 高途
    # 新能源汽车
    "NIO",    # 蔚来
    "LI",     # 理想汽车
    "XPEV",   # 小鹏汽车
    # 金融/券商
    "FUTU",   # 富途控股
    "TIGR",   # 老虎证券
    "FINV",   # 360数科
    "QFIN",   # 奇富科技
    # 科技/企业服务
    "NTES",   # 网易
    "ZTO",    # 中通快递
    "BEST",   # 百世集团
    "GDS",    # 万国数据
    "ATHM",   # 汽车之家
    # 生物医药
    "BGNE",   # 百济神州
    "ZLAB",   # 再鼎医药
    "HCM",    # 和黄医药
    # 房产/平台
    "BEKE",   # 贝壳找房
    "TME",    # 腾讯音乐
]

# 中文名称映射
TICKER_CN_NAMES = {
    "BABA": "阿里巴巴", "JD": "京东", "PDD": "拼多多",
    "VIPS": "唯品会", "YUMC": "百胜中国", "DADA": "达达",
    "BIDU": "百度", "BILI": "哔哩哔哩", "MOMO": "陌陌",
    "WB": "微博", "DOYU": "斗鱼", "HUYA": "虎牙",
    "TAL": "好未来", "EDU": "新东方", "GOTU": "高途",
    "NIO": "蔚来", "LI": "理想汽车", "XPEV": "小鹏汽车",
    "FUTU": "富途控股", "TIGR": "老虎证券", "FINV": "360数科",
    "QFIN": "奇富科技",
    "NTES": "网易", "ZTO": "中通快递", "BEST": "百世集团",
    "GDS": "万国数据", "ATHM": "汽车之家",
    "BGNE": "百济神州", "ZLAB": "再鼎医药", "HCM": "和黄医药",
    "BEKE": "贝壳找房", "TME": "腾讯音乐",
}


def fetch_stock_data(ticker: str) -> dict | None:
    """获取单只中概股的最新数据"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info or {}
        hist = stock.history(period="2d")
        
        if hist.empty:
            return None
        
        latest = hist.iloc[-1]
        prev_close = hist.iloc[-2]["Close"] if len(hist) > 1 else latest["Close"]
        
        current_price = round(float(latest["Close"]), 2)
        prev_close_val = round(float(prev_close), 2)
        change = round(current_price - prev_close_val, 2)
        change_pct = round((change / prev_close_val) * 100, 2) if prev_close_val else 0
        
        return {
            "ticker": ticker,
            "name_cn": TICKER_CN_NAMES.get(ticker, ""),
            "name_en": info.get("longName", info.get("shortName", ticker)),
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
            "price": current_price,
            "change": change,
            "change_pct": change_pct,
            "prev_close": prev_close_val,
            "open": round(float(latest["Open"]), 2),
            "high": round(float(latest["High"]), 2),
            "low": round(float(latest["Low"]), 2),
            "volume": int(latest["Volume"]),
            "market_cap": info.get("marketCap", 0),
            "pe_ratio": info.get("trailingPE", info.get("forwardPE")),
            "market_state": info.get("marketState", "UNKNOWN"),
            "currency": info.get("currency", "USD"),
        }
    except Exception as e:
        print(f"  {ticker} 获取失败: {e}")
        return None


def main():
    print(f"正在抓取中概股数据，共 {len(CHINA_ADR_TICKERS)} 只股票...")
    
    stocks = []
    for ticker in CHINA_ADR_TICKERS:
        print(f"  正在获取 {ticker}...")
        data = fetch_stock_data(ticker)
        if data:
            stocks.append(data)
    
    # 按涨跌幅排序
    stocks.sort(key=lambda x: x.get("change_pct", 0), reverse=True)
    
    # 统计涨跌家数
    up_count = sum(1 for s in stocks if s.get("change_pct", 0) > 0)
    down_count = sum(1 for s in stocks if s.get("change_pct", 0) < 0)
    flat_count = sum(1 for s in stocks if s.get("change_pct", 0) == 0)
    
    output = {
        "source": "Yahoo Finance (yfinance)",
        "description": "中概股（在美上市中国公司）最新行情数据",
        "market": "US (NYSE/NASDAQ)",
        "scraped_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_count": len(stocks),
        "summary": {
            "上涨": up_count,
            "下跌": down_count,
            "平盘": flat_count,
        },
        "data": stocks,
    }
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n数据已保存到 {OUTPUT_FILE}")
    print(f"共获取 {len(stocks)} 只中概股数据")
    print(f"上涨: {up_count} | 下跌: {down_count} | 平盘: {flat_count}")
    
    # 打印涨跌前5
    print(f"\n涨幅前5:")
    for s in stocks[:5]:
        print(f"  {s['name_cn']:6s} ({s['ticker']}) : ${s['price']:>8.2f}  {s['change_pct']:>+6.2f}%")
    print(f"\n跌幅前5:")
    for s in stocks[-5:]:
        print(f"  {s['name_cn']:6s} ({s['ticker']}) : ${s['price']:>8.2f}  {s['change_pct']:>+6.2f}%")


if __name__ == "__main__":
    main()
