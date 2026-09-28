package utils

import (
	"MomentLingo/common"
	"context"
	"errors"
	"fmt"
	"log/slog"
	"time"

	"github.com/redis/go-redis/v9"
)

type rdbUtil struct {
}

var Rdb rdbUtil

func panicErr(err error) {
	slog.Error("redis异常", "RedisError", err)
	panic(fmt.Errorf("redis异常 %w", err))
}

func (rdbUtil) Get(key string) *string {
	val, err := common.Redis.Get(context.TODO(), key).Result()

	if err != nil {
		// redis不存在该key
		if errors.Is(err, redis.Nil) {
			return nil
		}
		panicErr(err)
	}
	return &val
}

func (rdbUtil) SetEx(key string, val any, exp time.Duration) {
	if err := common.Redis.SetEx(context.TODO(), key, val, exp).Err(); err != nil {
		panicErr(err)
	}
}

func (rdbUtil) Del(key string) {
	if err := common.Redis.Del(context.TODO(), key).Err(); err != nil {
		panicErr(err)
	}
}

func (rdbUtil) ZAdd(key, member string, score float64) {
	if err := common.Redis.ZAdd(context.TODO(), key, redis.Z{Score: score, Member: member}).Err(); err != nil {
		panicErr(err)
	}
}

func (rdbUtil) ZRem(key, member string) {
	if err := common.Redis.ZRem(context.TODO(), key, member).Err(); err != nil {
		panicErr(err)
	}
}

func (rdbUtil) ZScore(key, member string) float64 {
	score, err := common.Redis.ZScore(context.TODO(), key, member).Result()
	if err != nil {
		panicErr(err)
	}
	return score
}

func (rdbUtil) Scan(pattern string) []string {
	iter := common.Redis.Scan(context.TODO(), 0, pattern, 20).Iterator()
	keys := make([]string, 0)
	for iter.Next(context.TODO()) {
		keys = append(keys, iter.Val())
	}

	if err := iter.Err(); err != nil {
		panicErr(err)
	}

	return keys
}

func (rdbUtil) HGetAll(key string) map[string]string {
	hm, err := common.Redis.HGetAll(context.TODO(), key).Result()
	if err != nil {
		panicErr(err)
	}
	return hm
}
