-- 基于 Tushare `dc_index` 接口输出参数设计
-- 文档: https://tushare.pro/document/2?doc_id=362
-- 方言: MySQL 8.0+

CREATE TABLE IF NOT EXISTS `dc_index` (
    `ts_code` VARCHAR(20) NOT NULL COMMENT '概念代码',
    `trade_date` CHAR(8) NOT NULL COMMENT '交易日期，格式YYYYMMDD',
    `name` VARCHAR(100) NOT NULL COMMENT '概念名称',
    `leading` VARCHAR(100) DEFAULT NULL COMMENT '领涨股票名称',
    `leading_code` VARCHAR(20) DEFAULT NULL COMMENT '领涨股票代码',
    `pct_change` DECIMAL(18,4) DEFAULT NULL COMMENT '涨跌幅',
    `leading_pct` DECIMAL(18,4) DEFAULT NULL COMMENT '领涨股票涨跌幅',
    `total_mv` DECIMAL(24,4) DEFAULT NULL COMMENT '总市值（万元）',
    `turnover_rate` DECIMAL(18,4) DEFAULT NULL COMMENT '换手率',
    `up_num` INT DEFAULT NULL COMMENT '上涨家数',
    `down_num` INT DEFAULT NULL COMMENT '下降家数',
    `idx_type` VARCHAR(30) DEFAULT NULL COMMENT '板块类型，行业板块、概念板块、地域板块',
    `level` VARCHAR(30) DEFAULT NULL COMMENT '行业层级',
    PRIMARY KEY (`trade_date`, `ts_code`),
    KEY `idx_dc_index_ts_code` (`ts_code`),
    KEY `idx_dc_index_name` (`name`),
    KEY `idx_dc_index_idx_type` (`idx_type`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COMMENT='东方财富概念板块分类';

