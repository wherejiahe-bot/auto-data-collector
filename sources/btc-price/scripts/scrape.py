"""
抓取比特币今日行情
使用 yfinance 获取 BTC-USD 实时数据
输出: data/btc-price.json
"""

import json
import os
import yfinance as yf
from datetime import datetime

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "btc-price.json")


def fetch_btc_price() -> dict:
    """获取比特币最新行情"""
    btc = yf.Ticker("BTC-USD")
    info = btc.info or {}
    hist = btc.history(period="5d")
    
    if hist.empty:
        return {}
    
    latest = hist.iloc[-1]
    prev_close = hist.iloc[-2]["Close"] if len(hist) > 1 else latest["Close"]
    
    # 计算24h涨跌
    close_24h_ago = hist.iloc[-2]["Close"] if len(hist) > 1 else latest["Close"]
    current_price = float(latest["Close"])
    change = round(current_price - float(close_24h_ago), 2)
    change_pct = round((change / float(close_24h_ago)) * 100, 2) if float(close_24h_ago) else 0
    
    # 7日数据
    week_high = float(hist["High"].max()) if len(hist) > 0 else current_price
    week_low = float(hist["Low"].min()) if len(hist) > 0 else current_price
    
    return {
        "symbol": "BTC-USD",
        "name": "Bitcoin",
        "name_cn": "比特币",
        "price": current_price,
        "change_24h": change,
        "change_24h_pct": change_pct,
        "high_24h": round(float(latest["High"]), 2),
        "low_24h": round(float(latest["Low"]), 2),
        "volume_24h": int(latest["Volume"]),
        "open_24h": round(float(latest["Open"]), 2),
        "market_cap": info.get("marketCap", 0),
        "circulating_supply": info.get("circulatingSupply", 0),
        "week_high": round(week_high, 2),
        "week_low": round(week_low, 2),
        "rank": info.get("marketCapRank", 0),
    }


def main():
    print("正在获取比特币行情...")
    
    data = fetch_btc_price()
    
    if not data:
        print("获取失败")
        return
    
    output = {
        "source": "Yahoo Finance (yfinance)",
        "description": "比特币 (BTC-USD) 今日行情",
        "currency": "USD",
        "scraped_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "data": data,
    }
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"数据已保存到 {OUTPUT_FILE}")
    print(f"BTC: ${data['price']:,.2f}  ({data['change_24h_pct']:+.2f}%)")


if __name__ == "__main__":
    main()
