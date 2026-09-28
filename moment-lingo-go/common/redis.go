package common

import (
	"MomentLingo/config"
	"context"
	"fmt"
	"time"

	"github.com/redis/go-redis/v9"
)

var Redis *redis.Client

func InitRedis(cfg config.RedisConfig) {
	Redis = redis.NewClient(&redis.Options{
		Addr:         fmt.Sprintf("%s:%d", cfg.Host, cfg.Port),
		Username:     cfg.Username,
		Password:     cfg.Password,
		DB:           cfg.DB,
		PoolSize:     20,               // 连接池大小
		MinIdleConns: 10,               // 最小空闲连接
		DialTimeout:  20 * time.Second, // 延长连接超时
		ReadTimeout:  20 * time.Second, // 延长读超时
		WriteTimeout: 20 * time.Second, // 延长写超时
	})

	ctx, cancel := context.WithTimeout(context.TODO(), 5*time.Second)
	defer cancel()

	_, err := Redis.Ping(ctx).Result()
	if err != nil {
		panic(fmt.Errorf("redis连接失败 %w", err))
	}
}
