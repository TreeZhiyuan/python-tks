-- 基于 Tushare `daily` 接口输出参数设计
-- 文档: https://tushare.pro/document/2?doc_id=27
-- 目标数据库: Cloudflare D1 (SQLite 语义)
-- 说明:
-- 1. D1 不支持 MySQL 风格的 ENGINE / CHARSET / COMMENT 语法
-- 2. 表注释和字段注释以 SQL 注释形式保留

-- 表: A股日线行情
CREATE TABLE IF NOT EXISTS daily (
    ts_code TEXT NOT NULL,          -- 股票代码
    trade_date TEXT NOT NULL,       -- 交易日期，格式 YYYYMMDD
    open_price REAL,                -- 开盘价
    high_price REAL,                -- 最高价
    low_price REAL,                 -- 最低价
    close_price REAL,               -- 收盘价
    pre_close REAL,                 -- 昨收价（除权价）
    change_amount REAL,             -- 涨跌额
    pct_chg REAL,                   -- 涨跌幅(%)
    vol REAL,                       -- 成交量(手)
    amount REAL,                    -- 成交额(千元)
    PRIMARY KEY (trade_date, ts_code)
);

-- 索引: 按股票代码查询
CREATE INDEX IF NOT EXISTS idx_daily_ts_code
ON daily (ts_code);
