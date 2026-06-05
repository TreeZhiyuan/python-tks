-- 基于 Tushare `moneyflow_ind_dc` 接口输出参数设计
-- 文档: https://tushare.pro/document/2?doc_id=344
-- 方言: MySQL 8.0+

CREATE TABLE IF NOT EXISTS `moneyflow_ind_dc` (
    `trade_date` CHAR(8) NOT NULL COMMENT '交易日期，格式YYYYMMDD',
    `content_type` VARCHAR(20) NOT NULL COMMENT '数据类型(行业、概念、地域)',
    `ts_code` VARCHAR(20) NOT NULL COMMENT 'DC板块代码（行业、概念、地域）',
    `name` VARCHAR(100) NOT NULL COMMENT '板块名称',
    `pct_change` DECIMAL(18,4) DEFAULT NULL COMMENT '板块涨跌幅(%)',
    `close_price` DECIMAL(18,4) DEFAULT NULL COMMENT '板块最新指数',
    `net_amount` DECIMAL(20,2) DEFAULT NULL COMMENT '今日主力净流入净额(元)',
    `net_amount_rate` DECIMAL(18,4) DEFAULT NULL COMMENT '今日主力净流入净占比%',
    `buy_elg_amount` DECIMAL(20,2) DEFAULT NULL COMMENT '今日超大单净流入净额(元)',
    `buy_elg_amount_rate` DECIMAL(18,4) DEFAULT NULL COMMENT '今日超大单净流入净占比%',
    `buy_lg_amount` DECIMAL(20,2) DEFAULT NULL COMMENT '今日大单净流入净额(元)',
    `buy_lg_amount_rate` DECIMAL(18,4) DEFAULT NULL COMMENT '今日大单净流入净占比%',
    `buy_md_amount` DECIMAL(20,2) DEFAULT NULL COMMENT '今日中单净流入净额(元)',
    `buy_md_amount_rate` DECIMAL(18,4) DEFAULT NULL COMMENT '今日中单净流入净占比%',
    `buy_sm_amount` DECIMAL(20,2) DEFAULT NULL COMMENT '今日小单净流入净额(元)',
    `buy_sm_amount_rate` DECIMAL(18,4) DEFAULT NULL COMMENT '今日小单净流入净占比%',
    `buy_sm_amount_stock` VARCHAR(100) DEFAULT NULL COMMENT '今日主力净流入最大股',
    `rank_no` INT DEFAULT NULL COMMENT '序号',
    PRIMARY KEY (`trade_date`, `content_type`, `ts_code`),
    KEY `idx_moneyflow_ind_dc_ts_code` (`ts_code`),
    KEY `idx_moneyflow_ind_dc_name` (`name`),
    KEY `idx_moneyflow_ind_dc_content_type` (`content_type`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COMMENT='东财概念及行业板块每日资金流向';
