-- 基于 Tushare `dc_index` 接口输出参数设计
-- 文档: https://tushare.pro/document/2?doc_id=362
-- 目标数据库: Cloudflare D1 (SQLite 语义)
-- 说明:
-- 1. D1 不支持 MySQL 风格的 ENGINE / CHARSET / COMMENT 语法
-- 2. 表注释和字段注释以 SQL 注释形式保留

-- 表: 东方财富概念板块分类
CREATE TABLE IF NOT EXISTS dc_index (
    ts_code TEXT NOT NULL,       -- 概念代码
    trade_date TEXT NOT NULL,    -- 交易日期，格式 YYYYMMDD
    name TEXT NOT NULL,          -- 概念名称
    leading TEXT,                -- 领涨股票名称
    leading_code TEXT,           -- 领涨股票代码
    pct_change REAL,             -- 涨跌幅
    leading_pct REAL,            -- 领涨股票涨跌幅
    total_mv REAL,               -- 总市值（万元）
    turnover_rate REAL,          -- 换手率
    up_num INTEGER,              -- 上涨家数
    down_num INTEGER,            -- 下降家数
    idx_type TEXT,               -- 板块类型，行业板块、概念板块、地域板块
    level TEXT,                  -- 行业层级
    PRIMARY KEY (trade_date, ts_code)
);

-- 索引: 按概念代码查询
CREATE INDEX IF NOT EXISTS idx_dc_index_ts_code
ON dc_index (ts_code);

-- 索引: 按概念名称查询
CREATE INDEX IF NOT EXISTS idx_dc_index_name
ON dc_index (name);

-- 索引: 按板块类型查询
CREATE INDEX IF NOT EXISTS idx_dc_index_idx_type
ON dc_index (idx_type);

