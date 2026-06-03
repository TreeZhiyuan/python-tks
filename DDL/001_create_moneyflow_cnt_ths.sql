-- 基于 Tushare `moneyflow_cnt_ths` 接口输出参数设计
-- 文档: https://tushare.pro/document/2?doc_id=371
-- 方言: MySQL 8.0+

CREATE TABLE IF NOT EXISTS `moneyflow_cnt_ths` (
    `trade_date` CHAR(8) NOT NULL COMMENT '交易日期，格式YYYYMMDD',
    `ts_code` VARCHAR(20) NOT NULL COMMENT '板块代码',
    `name` VARCHAR(100) NOT NULL COMMENT '板块名称',
    `lead_stock` VARCHAR(100) DEFAULT NULL COMMENT '领涨股票名称',
    `close_price` DECIMAL(18,4) DEFAULT NULL COMMENT '最新价',
    `pct_change` DECIMAL(18,4) DEFAULT NULL COMMENT '行业涨跌幅',
    `industry_index` DECIMAL(18,4) DEFAULT NULL COMMENT '板块指数点位',
    `company_num` INT DEFAULT NULL COMMENT '公司数量',
    `pct_change_stock` DECIMAL(18,4) DEFAULT NULL COMMENT '领涨股涨跌幅',
    `net_buy_amount` DECIMAL(18,4) DEFAULT NULL COMMENT '流入资金(亿元)',
    `net_sell_amount` DECIMAL(18,4) DEFAULT NULL COMMENT '流出资金(亿元)',
    `net_amount` DECIMAL(18,4) DEFAULT NULL COMMENT '净额(亿元)',
    PRIMARY KEY (`trade_date`, `ts_code`),
    KEY `idx_moneyflow_cnt_ths_ts_code` (`ts_code`),
    KEY `idx_moneyflow_cnt_ths_name` (`name`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COMMENT='同花顺概念板块每日资金流向';
