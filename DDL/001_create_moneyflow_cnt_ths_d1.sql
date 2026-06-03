-- 基于 Tushare `moneyflow_cnt_ths` 接口输出参数设计
-- 文档: https://tushare.pro/document/2?doc_id=371
-- 目标数据库: Cloudflare D1 (SQLite 语义)
-- 说明:
-- 1. D1 不支持 MySQL 风格的 ENGINE / CHARSET / COMMENT 语法
-- 2. 表注释和字段注释以 SQL 注释形式保留

-- 表: 同花顺概念板块每日资金流向
CREATE TABLE IF NOT EXISTS moneyflow_cnt_ths (
    trade_date TEXT NOT NULL,         -- 交易日期，格式 YYYYMMDD
    ts_code TEXT NOT NULL,            -- 板块代码
    name TEXT NOT NULL,               -- 板块名称
    lead_stock TEXT,                  -- 领涨股票名称
    close_price REAL,                 -- 最新价
    pct_change REAL,                  -- 行业涨跌幅
    industry_index REAL,              -- 板块指数点位
    company_num INTEGER,              -- 公司数量
    pct_change_stock REAL,            -- 领涨股涨跌幅
    net_buy_amount REAL,              -- 流入资金(亿元)
    net_sell_amount REAL,             -- 流出资金(亿元)
    net_amount REAL,                  -- 净额(亿元)
    PRIMARY KEY (trade_date, ts_code)
);

-- 索引: 按板块代码查询
CREATE INDEX IF NOT EXISTS idx_moneyflow_cnt_ths_ts_code
ON moneyflow_cnt_ths (ts_code);

-- 索引: 按板块名称查询
CREATE INDEX IF NOT EXISTS idx_moneyflow_cnt_ths_name
ON moneyflow_cnt_ths (name);
