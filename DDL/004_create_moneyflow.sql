-- 基于 Tushare `moneyflow` 接口输出参数设计
-- 文档: https://tushare.pro/document/2?doc_id=170
-- 方言: MySQL 8.0+

CREATE TABLE IF NOT EXISTS `moneyflow` (
    `ts_code` VARCHAR(20) NOT NULL COMMENT 'TS代码',
    `trade_date` CHAR(8) NOT NULL COMMENT '交易日期，格式YYYYMMDD',
    `buy_sm_vol` BIGINT DEFAULT NULL COMMENT '小单买入量(手)',
    `buy_sm_amount` DECIMAL(20,4) DEFAULT NULL COMMENT '小单买入金额(万元)',
    `sell_sm_vol` BIGINT DEFAULT NULL COMMENT '小单卖出量(手)',
    `sell_sm_amount` DECIMAL(20,4) DEFAULT NULL COMMENT '小单卖出金额(万元)',
    `buy_md_vol` BIGINT DEFAULT NULL COMMENT '中单买入量(手)',
    `buy_md_amount` DECIMAL(20,4) DEFAULT NULL COMMENT '中单买入金额(万元)',
    `sell_md_vol` BIGINT DEFAULT NULL COMMENT '中单卖出量(手)',
    `sell_md_amount` DECIMAL(20,4) DEFAULT NULL COMMENT '中单卖出金额(万元)',
    `buy_lg_vol` BIGINT DEFAULT NULL COMMENT '大单买入量(手)',
    `buy_lg_amount` DECIMAL(20,4) DEFAULT NULL COMMENT '大单买入金额(万元)',
    `sell_lg_vol` BIGINT DEFAULT NULL COMMENT '大单卖出量(手)',
    `sell_lg_amount` DECIMAL(20,4) DEFAULT NULL COMMENT '大单卖出金额(万元)',
    `buy_elg_vol` BIGINT DEFAULT NULL COMMENT '特大单买入量(手)',
    `buy_elg_amount` DECIMAL(20,4) DEFAULT NULL COMMENT '特大单买入金额(万元)',
    `sell_elg_vol` BIGINT DEFAULT NULL COMMENT '特大单卖出量(手)',
    `sell_elg_amount` DECIMAL(20,4) DEFAULT NULL COMMENT '特大单卖出金额(万元)',
    `net_mf_vol` BIGINT DEFAULT NULL COMMENT '净流入量(手)',
    `net_mf_amount` DECIMAL(20,4) DEFAULT NULL COMMENT '净流入额(万元)',
    PRIMARY KEY (`trade_date`, `ts_code`),
    KEY `idx_moneyflow_ts_code` (`ts_code`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COMMENT='沪深A股个股每日资金流向';
