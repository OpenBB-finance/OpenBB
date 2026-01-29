"""模型字段的常用描述。"""

QUERY_DESCRIPTIONS = {
    "symbol": "获取数据的代码。",
    "start_date": "数据的开始日期，格式为 YYYY-MM-DD。",
    "end_date": "数据的结束日期，格式为 YYYY-MM-DD。",
    "interval": "要返回的数据的时间间隔。",
    "period": "要返回的数据的时间段。",
    "date": "获取数据的特定日期。",
    "limit": "要返回的数据条目数。",
    "country": "获取数据的国家。",
    "countries": "获取数据的国家。",
    "units": "数据的测量单位。",
    "frequency": "数据的频率。",
}

DATA_DESCRIPTIONS = {
    "symbol": "代表数据中请求实体的代码。",
    "cik": "请求实体的中央索引键 (CIK)。",
    "date": "数据日期。",
    "open": "开盘价。",
    "high": "最高价。",
    "low": "最低价。",
    "close": "收盘价。",
    "volume": "交易量。",
    "adj_close": "调整后的收盘价。",
    "vwap": "在此期间的成交量加权平均价格。",
    "prev_close": "前一个收盘价。",
}
