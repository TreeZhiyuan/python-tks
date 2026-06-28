-- 基于 Tushare `ths_index` 接口输出参数设计
-- 文档: https://tushare.pro/document/2?doc_id=259
-- 目标数据库: Cloudflare D1 (SQLite 语义)
-- 说明:
-- 1. D1 不支持 MySQL 风格的 ENGINE / CHARSET / COMMENT 语法
-- 2. 表注释和字段注释以 SQL 注释形式保留

-- 表: 同花顺概念和行业指数分类
CREATE TABLE IF NOT EXISTS ths_index (
    ts_code TEXT NOT NULL,       -- 代码
    name TEXT NOT NULL,          -- 名称
    count INTEGER,               -- 成分个数
    exchange TEXT,               -- 交易所
    list_date TEXT,              -- 上市日期，格式 YYYYMMDD
    type TEXT,                   -- 指数类型，N概念指数，S特色指数等
    PRIMARY KEY (ts_code)
);

-- 索引: 按名称查询
CREATE INDEX IF NOT EXISTS idx_ths_index_name
ON ths_index (name);

-- 索引: 按交易所查询
CREATE INDEX IF NOT EXISTS idx_ths_index_exchange
ON ths_index (exchange);

-- 索引: 按指数类型查询
CREATE INDEX IF NOT EXISTS idx_ths_index_type
ON ths_index (type);

