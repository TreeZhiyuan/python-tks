-- 基于 Tushare `ths_index` 接口输出参数设计
-- 文档: https://tushare.pro/document/2?doc_id=259
-- 方言: MySQL 8.0+

CREATE TABLE IF NOT EXISTS `ths_index` (
    `ts_code` VARCHAR(20) NOT NULL COMMENT '代码',
    `name` VARCHAR(100) NOT NULL COMMENT '名称',
    `count` INT DEFAULT NULL COMMENT '成分个数',
    `exchange` VARCHAR(20) DEFAULT NULL COMMENT '交易所',
    `list_date` CHAR(8) DEFAULT NULL COMMENT '上市日期，格式YYYYMMDD',
    `type` VARCHAR(20) DEFAULT NULL COMMENT '指数类型，N概念指数，S特色指数等',
    PRIMARY KEY (`ts_code`),
    KEY `idx_ths_index_name` (`name`),
    KEY `idx_ths_index_exchange` (`exchange`),
    KEY `idx_ths_index_type` (`type`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COMMENT='同花顺概念和行业指数分类';

