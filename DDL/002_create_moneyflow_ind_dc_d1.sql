-- 基于 Tushare `moneyflow_ind_dc` 接口输出参数设计
-- 文档: https://tushare.pro/document/2?doc_id=344
-- 目标数据库: Cloudflare D1 (SQLite 语义)
-- 说明:
-- 1. D1 不支持 MySQL 风格的 ENGINE / CHARSET / COMMENT 语法
-- 2. 表注释和字段注释以 SQL 注释形式保留

-- 表: 东财概念及行业板块每日资金流向
CREATE TABLE IF NOT EXISTS moneyflow_ind_dc (
    trade_date TEXT NOT NULL,             -- 交易日期，格式 YYYYMMDD
    content_type TEXT NOT NULL,           -- 数据类型(行业、概念、地域)
    ts_code TEXT NOT NULL,                -- DC板块代码（行业、概念、地域）
    name TEXT NOT NULL,                   -- 板块名称
    pct_change REAL,                      -- 板块涨跌幅(%)
    close_price REAL,                     -- 板块最新指数
    net_amount REAL,                      -- 今日主力净流入净额(元)
    net_amount_rate REAL,                 -- 今日主力净流入净占比%
    buy_elg_amount REAL,                  -- 今日超大单净流入净额(元)
    buy_elg_amount_rate REAL,             -- 今日超大单净流入净占比%
    buy_lg_amount REAL,                   -- 今日大单净流入净额(元)
    buy_lg_amount_rate REAL,              -- 今日大单净流入净占比%
    buy_md_amount REAL,                   -- 今日中单净流入净额(元)
    buy_md_amount_rate REAL,              -- 今日中单净流入净占比%
    buy_sm_amount REAL,                   -- 今日小单净流入净额(元)
    buy_sm_amount_rate REAL,              -- 今日小单净流入净占比%
    buy_sm_amount_stock TEXT,             -- 今日主力净流入最大股
    rank_no INTEGER,                      -- 序号
    PRIMARY KEY (trade_date, content_type, ts_code)
);

-- 索引: 按板块代码查询
CREATE INDEX IF NOT EXISTS idx_moneyflow_ind_dc_ts_code
ON moneyflow_ind_dc (ts_code);

-- 索引: 按板块名称查询
CREATE INDEX IF NOT EXISTS idx_moneyflow_ind_dc_name
ON moneyflow_ind_dc (name);

-- 索引: 按数据类型查询
CREATE INDEX IF NOT EXISTS idx_moneyflow_ind_dc_content_type
ON moneyflow_ind_dc (content_type);
