-- 基于 Tushare `moneyflow_dc` 接口输出参数设计
-- 文档: https://tushare.pro/document/2?doc_id=349
-- 目标数据库: Cloudflare D1 (SQLite 语义)
-- 说明:
-- 1. D1 不支持 MySQL 风格的 ENGINE / CHARSET / COMMENT 语法
-- 2. 表注释和字段注释以 SQL 注释形式保留

-- 表: 东方财富个股每日资金流向
CREATE TABLE IF NOT EXISTS moneyflow_dc (
    trade_date TEXT NOT NULL,       -- 交易日期，格式 YYYYMMDD
    ts_code TEXT NOT NULL,          -- 股票代码
    name TEXT,                      -- 股票名称
    pct_change REAL,                -- 涨跌幅
    close_price REAL,               -- 最新价
    net_amount REAL,                -- 今日主力净流入额(万元)
    net_amount_rate REAL,           -- 今日主力净流入净占比(%)
    buy_elg_amount REAL,            -- 今日超大单净流入额(万元)
    buy_elg_amount_rate REAL,       -- 今日超大单净流入占比(%)
    buy_lg_amount REAL,             -- 今日大单净流入额(万元)
    buy_lg_amount_rate REAL,        -- 今日大单净流入占比(%)
    buy_md_amount REAL,             -- 今日中单净流入额(万元)
    buy_md_amount_rate REAL,        -- 今日中单净流入占比(%)
    buy_sm_amount REAL,             -- 今日小单净流入额(万元)
    buy_sm_amount_rate REAL,        -- 今日小单净流入占比(%)
    PRIMARY KEY (trade_date, ts_code)
);

-- 索引: 按股票代码查询
CREATE INDEX IF NOT EXISTS idx_moneyflow_dc_ts_code
ON moneyflow_dc (ts_code);

-- 索引: 按股票名称查询
CREATE INDEX IF NOT EXISTS idx_moneyflow_dc_name
ON moneyflow_dc (name);
