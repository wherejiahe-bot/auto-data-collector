# auto-data-collector

自动化数据采集中心 - 合并多个 API 数据源。

## 数据源列表

| 源目录 | 原仓库 | 数据内容 |
|--------|--------|----------|
| `sources/btc-price/` | btc-price | Bitcoin 价格数据 |
| `sources/china-adr-data/` | china-adr-data | 中概股 ADR 数据 |
| `sources/china-finance-news/` | china-finance-news | 国内财经新闻 |
| `sources/china-stock-daily/` | china-stock-daily | A 股市场每日数据 |
| `sources/china-tt-news/` | china-tt-news | 中国乒乓球新闻 |
| `sources/military-news/` | military-news | 国际军事新闻 |
| `sources/numbeo-income-data/` | numbeo-income-data | 全球月薪数据 |
| `sources/oil-price/` | oil-price | 国际油价数据 |
| `sources/yt-trending/` | yt-trending | YouTube 热门趋势 |

## 目录结构

```
.github/workflows/    # 各数据源的 GitHub Actions 工作流
sources/{name}/       # 各数据源的脚本、数据和说明
  scripts/scrape.py   # 抓取脚本
  data/               # 采集的数据文件
  README.md           # 数据源说明
README.md            # 本文件（总说明）
```

## 自动化

每个数据源有独立的 GitHub Actions 工作流，按各自调度频率自动运行。
