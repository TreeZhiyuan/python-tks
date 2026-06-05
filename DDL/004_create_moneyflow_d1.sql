-- 基于 Tushare `moneyflow` 接口输出参数设计
-- 文档: https://tushare.pro/document/2?doc_id=170
-- 目标数据库: Cloudflare D1 (SQLite 语义)
-- 说明:
-- 1. D1 不支持 MySQL 风格的 ENGINE / CHARSET / COMMENT 语法
-- 2. 表注释和字段注释以 SQL 注释形式保留

-- 表: 沪深A股个股每日资金流向
CREATE TABLE IF NOT EXISTS moneyflow (
    ts_code TEXT NOT NULL,          -- TS代码
    trade_date TEXT NOT NULL,       -- 交易日期，格式 YYYYMMDD
    buy_sm_vol INTEGER,             -- 小单买入量(手)
    buy_sm_amount REAL,             -- 小单买入金额(万元)
    sell_sm_vol INTEGER,            -- 小单卖出量(手)
    sell_sm_amount REAL,            -- 小单卖出金额(万元)
    buy_md_vol INTEGER,             -- 中单买入量(手)
    buy_md_amount REAL,             -- 中单买入金额(万元)
    sell_md_vol INTEGER,            -- 中单卖出量(手)
    sell_md_amount REAL,            -- 中单卖出金额(万元)
    buy_lg_vol INTEGER,             -- 大单买入量(手)
    buy_lg_amount REAL,             -- 大单买入金额(万元)
    sell_lg_vol INTEGER,            -- 大单卖出量(手)
    sell_lg_amount REAL,            -- 大单卖出金额(万元)
    buy_elg_vol INTEGER,            -- 特大单买入量(手)
    buy_elg_amount REAL,            -- 特大单买入金额(万元)
    sell_elg_vol INTEGER,           -- 特大单卖出量(手)
    sell_elg_amount REAL,           -- 特大单卖出金额(万元)
    net_mf_vol INTEGER,             -- 净流入量(手)
    net_mf_amount REAL,             -- 净流入额(万元)
    PRIMARY KEY (trade_date, ts_code)
);

-- 索引: 按股票代码查询
CREATE INDEX IF NOT EXISTS idx_moneyflow_ts_code
ON moneyflow (ts_code);
