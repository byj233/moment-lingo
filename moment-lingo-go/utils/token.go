package utils

import (
	"fmt"
	"time"
)

type tokenManagerUtil struct{}

var TokenManager tokenManagerUtil

func (tokenManagerUtil) Add(userId int64) string {
	token := UUID()

	// token -> userId 映射
	Rdb.SetEx(fmt.Sprintf("token:%s", token), userId, time.Hour*24*30)
	// 登录历史缓存
	Rdb.ZAdd(fmt.Sprintf("user:login:%d", userId), token, float64(Timestamp()))
	return token
}

func (tokenManagerUtil) Remove(userId int64, token string) {
	Rdb.Del(token)
	Rdb.ZRem(fmt.Sprintf("user:login:%d", userId), token)
}

func (tokenManagerUtil) Validate(token string) *int64 {
	userId := Rdb.Get(fmt.Sprintf("token:%s", token))
	if userId == nil {
		return nil
	}
	return new(StrToInt[int64](*userId))
}
