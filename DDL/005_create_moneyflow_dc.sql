-- 基于 Tushare `moneyflow_dc` 接口输出参数设计
-- 文档: https://tushare.pro/document/2?doc_id=349
-- 方言: MySQL 8.0+

CREATE TABLE IF NOT EXISTS `moneyflow_dc` (
    `trade_date` CHAR(8) NOT NULL COMMENT '交易日期，格式YYYYMMDD',
    `ts_code` VARCHAR(20) NOT NULL COMMENT '股票代码',
    `name` VARCHAR(100) DEFAULT NULL COMMENT '股票名称',
    `pct_change` DECIMAL(18,4) DEFAULT NULL COMMENT '涨跌幅',
    `close_price` DECIMAL(18,4) DEFAULT NULL COMMENT '最新价',
    `net_amount` DECIMAL(20,4) DEFAULT NULL COMMENT '今日主力净流入额(万元)',
    `net_amount_rate` DECIMAL(18,4) DEFAULT NULL COMMENT '今日主力净流入净占比(%)',
    `buy_elg_amount` DECIMAL(20,4) DEFAULT NULL COMMENT '今日超大单净流入额(万元)',
    `buy_elg_amount_rate` DECIMAL(18,4) DEFAULT NULL COMMENT '今日超大单净流入占比(%)',
    `buy_lg_amount` DECIMAL(20,4) DEFAULT NULL COMMENT '今日大单净流入额(万元)',
    `buy_lg_amount_rate` DECIMAL(18,4) DEFAULT NULL COMMENT '今日大单净流入占比(%)',
    `buy_md_amount` DECIMAL(20,4) DEFAULT NULL COMMENT '今日中单净流入额(万元)',
    `buy_md_amount_rate` DECIMAL(18,4) DEFAULT NULL COMMENT '今日中单净流入占比(%)',
    `buy_sm_amount` DECIMAL(20,4) DEFAULT NULL COMMENT '今日小单净流入额(万元)',
    `buy_sm_amount_rate` DECIMAL(18,4) DEFAULT NULL COMMENT '今日小单净流入占比(%)',
    PRIMARY KEY (`trade_date`, `ts_code`),
    KEY `idx_moneyflow_dc_ts_code` (`ts_code`),
    KEY `idx_moneyflow_dc_name` (`name`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COMMENT='东方财富个股每日资金流向';
