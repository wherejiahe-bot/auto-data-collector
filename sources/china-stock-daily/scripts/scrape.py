"""
抓取A股今日行情数据
使用 yfinance 获取上证指数、深证成指、创业板指等主要指数数据
输出: data/china-stock-daily.json
"""

import json
import os
import yfinance as yf
from datetime import datetime

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "china-stock-daily.json")

# A股主要指数
INDICES = [
    {"symbol": "000001.SS", "name": "上证指数", "name_cn": "上证指数"},
    {"symbol": "399001.SZ", "name": "SZSE Component Index", "name_cn": "深证成指"},
    {"symbol": "399006.SZ", "name": "ChiNext Index", "name_cn": "创业板指"},
    {"symbol": "000688.SS", "name": "STAR 50 Index", "name_cn": "科创50"},
    {"symbol": "000300.SS", "name": "CSI 300 Index", "name_cn": "沪深300"},
]

# 板块表现数据（通过 ETF 或代表性个股估算）
SECTOR_ETFS = {
    "银行": "512800.SS",
    "证券": "512880.SS",
    "白酒": "512690.SS",
    "医药": "512010.SS",
    "新能源": "516160.SS",
    "半导体": "512480.SS",
    "军工": "512660.SS",
}


def fetch_index_data(symbol: str) -> dict | None:
    """获取指数当日数据"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="5d")
        if hist.empty:
            return None
        
        latest = hist.iloc[-1]
        prev_close = hist.iloc[-2]["Close"] if len(hist) > 1 else latest["Close"]
        
        current = round(float(latest["Close"]), 2)
        prev = round(float(prev_close), 2)
        change = round(current - prev, 2)
        change_pct = round((change / prev) * 100, 2) if prev else 0
        
        return {
            "price": current,
            "change": change,
            "change_pct": change_pct,
            "open": round(float(latest["Open"]), 2),
            "high": round(float(latest["High"]), 2),
            "low": round(float(latest["Low"]), 2),
            "volume": int(latest["Volume"]),
        }
    except Exception as e:
        print(f"  {symbol} 获取失败: {e}")
        return None


def fetch_sector_data() -> dict:
    """获取板块涨跌数据"""
    sectors = {}
    for name, etf_symbol in SECTOR_ETFS.items():
        try:
            ticker = yf.Ticker(etf_symbol)
            hist = ticker.history(period="5d")
            if hist.empty:
                continue
            latest = hist.iloc[-1]
            prev_close = hist.iloc[-2]["Close"] if len(hist) > 1 else latest["Close"]
            current = round(float(latest["Close"]), 2)
            prev = round(float(prev_close), 2)
            change_pct = round(((current - prev) / prev) * 100, 2) if prev else 0
            sectors[name] = change_pct
        except:
            continue
    return sectors


def get_market_sentiment(indices: list) -> str:
    """根据指数表现判断市场情绪"""
    if not indices:
        return "数据不足"
    
    sh_index = next((i for i in indices if i["name_cn"] == "上证指数"), None)
    if not sh_index:
        return "中性"
    
    pct = sh_index.get("change_pct", 0)
    if pct >= 1.5:
        return "强势上涨 📈"
    elif pct >= 0.5:
        return "温和上涨 ↗️"
    elif pct > -0.5:
        return "窄幅震荡 ➡️"
    elif pct > -1.5:
        return "温和下跌 ↘️"
    else:
        return "明显下跌 📉"


def main():
    print("正在获取A股今日行情...")
    
    # 获取指数数据
    index_results = []
    for idx in INDICES:
        print(f"  正在获取 {idx['name_cn']}...")
        data = fetch_index_data(idx["symbol"])
        if data:
            index_results.append({
                "symbol": idx["symbol"],
                "name": idx["name"],
                "name_cn": idx["name_cn"],
                **data,
            })
    
    # 获取板块数据
    print("  正在获取板块数据...")
    sectors = fetch_sector_data()
    
    # 市场情绪
    sentiment = get_market_sentiment(index_results)
    
    # 涨跌家数（估算）
    up_count = sum(1 for s in sectors.values() if s > 0)
    down_count = sum(1 for s in sectors.values() if s < 0)
    
    # 今日亮点与热点
    hot_sectors = []
    cold_sectors = []
    for name, pct in sorted(sectors.items(), key=lambda x: x[1], reverse=True):
        if pct > 0:
            hot_sectors.append(f"{name}({pct:+.2f}%)")
        else:
            cold_sectors.append(f"{name}({pct:+.2f}%)")
    
    output = {
        "source": "Yahoo Finance (yfinance)",
        "description": "A股今日行情解读",
        "market": "A股 (上海/深圳)",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "scraped_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "market_sentiment": sentiment,
        "indices": index_results,
        "sectors": sectors,
        "summary": {
            "sentiment": sentiment,
            "hot_sectors": hot_sectors[:3],
            "cold_sectors": cold_sectors[:3],
            "advance_decline": f"上涨板块 {up_count} 个 / 下跌板块 {down_count} 个",
        },
    }
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n数据已保存到 {OUTPUT_FILE}")
    print(f"\n市场情绪: {sentiment}")
    if index_results:
        sh = index_results[0]
        print(f"上证指数: {sh['price']} ({sh['change_pct']:+.2f}%)")
    if hot_sectors:
        print(f"领涨板块: {', '.join(hot_sectors[:3])}")
    if cold_sectors:
        print(f"领跌板块: {', '.join(cold_sectors[:3])}")


if __name__ == "__main__":
    main()
