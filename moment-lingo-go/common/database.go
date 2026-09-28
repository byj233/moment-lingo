package common

import (
	"MomentLingo/config"
	"fmt"
	"time"

	"github.com/bwmarrin/snowflake"
	"gorm.io/driver/mysql"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

var DB *gorm.DB

func InitDB(cfg config.DBConfig) {
	dsn := fmt.Sprintf(
		"%s:%s@tcp(%s:%d)/%s?charset=utf8mb4&parseTime=True&loc=Local",
		cfg.Username,
		cfg.Password,
		cfg.Host,
		cfg.Port,
		cfg.DB,
	)

	gormConfig := &gorm.Config{
		// 日志级别：开发环境用Info，生产环境用Warn（减少日志输出）
		Logger: logger.Default.LogMode(logger.Info),
		// 禁用默认事务（提高查询性能，非必须）
		SkipDefaultTransaction: true,
	}

	db, err := gorm.Open(mysql.Open(dsn), gormConfig)
	registerTimestampIDCallback(db)

	if err != nil {
		panic(fmt.Errorf("数据库连接失败 %w", err))
	}

	sqlDB, err := db.DB()
	if err != nil {
		panic(fmt.Errorf("数据库连接失败 %w", err))
	} else if err = sqlDB.Ping(); err != nil {
		panic(fmt.Errorf("数据库连接失败 %w", err))
	}

	// 设置连接池参数
	sqlDB.SetMaxOpenConns(100)
	sqlDB.SetMaxIdleConns(20)
	sqlDB.SetConnMaxLifetime(30 * time.Minute)
	sqlDB.SetConnMaxIdleTime(10 * time.Minute)

	DB = db
}

func generateSnowflakeId(db *gorm.DB) {
	node, err := snowflake.NewNode(0)
	if err != nil {
		panic(fmt.Errorf("雪花算法节点初始化失败 %w", err))
	}

	if db.Statement.Schema != nil {
		for _, field := range db.Statement.Schema.Fields {
			if field.PrimaryKey {
				id := node.Generate().Int64()
				db.Statement.SetColumn(field.Name, id)
			}
		}
	}
}

func registerTimestampIDCallback(db *gorm.DB) {
	err := db.Callback().Create().Before("gorm:create").Register("snowflake_id", generateSnowflakeId)
	if err != nil {
		panic(fmt.Errorf("雪花算法回调注册失败 %w", err))
	}
}
