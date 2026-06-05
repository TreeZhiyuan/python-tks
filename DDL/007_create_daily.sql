-- 基于 Tushare `daily` 接口输出参数设计
-- 文档: https://tushare.pro/document/2?doc_id=27
-- 方言: MySQL 8.0+

CREATE TABLE IF NOT EXISTS `daily` (
    `ts_code` VARCHAR(20) NOT NULL COMMENT '股票代码',
    `trade_date` CHAR(8) NOT NULL COMMENT '交易日期，格式YYYYMMDD',
    `open_price` DECIMAL(18,4) DEFAULT NULL COMMENT '开盘价',
    `high_price` DECIMAL(18,4) DEFAULT NULL COMMENT '最高价',
    `low_price` DECIMAL(18,4) DEFAULT NULL COMMENT '最低价',
    `close_price` DECIMAL(18,4) DEFAULT NULL COMMENT '收盘价',
    `pre_close` DECIMAL(18,4) DEFAULT NULL COMMENT '昨收价（除权价）',
    `change_amount` DECIMAL(18,4) DEFAULT NULL COMMENT '涨跌额',
    `pct_chg` DECIMAL(18,4) DEFAULT NULL COMMENT '涨跌幅(%)',
    `vol` DECIMAL(24,4) DEFAULT NULL COMMENT '成交量(手)',
    `amount` DECIMAL(24,4) DEFAULT NULL COMMENT '成交额(千元)',
    PRIMARY KEY (`trade_date`, `ts_code`),
    KEY `idx_daily_ts_code` (`ts_code`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COMMENT='A股日线行情';
