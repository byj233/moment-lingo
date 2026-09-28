package utils

import (
	"MomentLingo/errs"
	"errors"
	"fmt"
	"log/slog"
	"reflect"
	"strconv"
	"time"

	"github.com/bwmarrin/snowflake"
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

type H map[string]any

func (h H) JSON() string {
	return JSON.Stringify(h)
}

func BuildPageEntity(current, pages, total int, data any) map[string]any {
	return map[string]any{
		"current": current,
		"pages":   pages,
		"total":   total,
		"data":    data,
	}
}

func ShouldBindJSON(c *gin.Context, val any) {
	if err := c.ShouldBindJSON(&val); err != nil {
		slog.Error("参数错误", "ErrorWithMsg", err.Error())
		panic(errs.CustomError{Code: 422, Msg: fmt.Sprintf("参数错误 %v", err)})
	}
}

func GenerateSnowflakeId() int64 {
	node, _ := snowflake.NewNode(0)
	return node.Generate().Int64()
}

func StrToInt[T ~int | ~int64](val string) T {
	var zero T
	switch any(zero).(type) {
	case int:
		num, err := strconv.Atoi(val)
		if err != nil {
			panic(fmt.Errorf("%v无法转化为int类型 %w", val, err))
		}
		return T(num)
	case int64:
		num, err := strconv.ParseInt(val, 10, 64)
		if err != nil {
			panic(fmt.Errorf("%v无法转化为int类型 %w", val, err))
		}
		return T(num)
	default:
		panic(fmt.Errorf("%v无法转化为int类型", val))
	}
}

func IntToStr[T ~int | ~int64](val T) string {
	return strconv.FormatInt(int64(val), 10)
}

func Timestamp() int64 {
	utcNow := time.Now().UTC()
	u := utcNow.Add(8 * time.Hour)
	return u.UnixMilli()
}

func TimestampWithExpire(exp time.Duration) int64 {
	utcNow := time.Now().UTC()
	u := utcNow.Add(8 * time.Hour)
	if exp > 0 {
		u = u.Add(exp)
	}

	return u.UnixMilli()
}

func GetUserId(c *gin.Context) int64 {
	userId, _ := c.Get("userId")
	if userId == nil {
		panic(errs.CustomError{Code: 403, Msg: "权限不足，无法访问"})
	}
	return userId.(int64)
}

func UUID() string {
	v4, err := uuid.NewRandom()
	if err != nil {
		slog.Error("uuid无法成成", "UUIDError", err)
		panic(fmt.Errorf("uuid无法成成 %w", err))
	}
	return v4.String()
}

func getValue[T ~string | ~int | ~int64](getter func() string, key string) T {
	val := getter()

	if val == "" {
		panic(errs.CustomError{Code: 500, Msg: fmt.Sprintf("%s不能为空", key)})
	}

	var zero T
	switch any(zero).(type) {
	case string:
		return any(val).(T)
	case int:
		valInt := StrToInt[int](val)
		return any(valInt).(T)
	case int64:
		valInt := StrToInt[int64](val)
		return any(valInt).(T)
	default:
		panic(errors.New("不支持的类型"))
	}
}

func Query[T ~string | ~int | ~int64](c *gin.Context, key string) T {
	return getValue[T](func() string {
		return c.Query(key)
	}, key)
}

func Param[T ~string | ~int | ~int64](c *gin.Context, key string) T {
	return getValue[T](func() string {
		return c.Param(key)
	}, key)
}

// IsZero 判断是否为零值或指针是否为nil
func IsZero[T any](v T) bool {
	val := reflect.ValueOf(v)

	// 解包所有指针（支持 *T, **T, ***T 都能解）
	for val.Kind() == reflect.Ptr {
		if val.IsNil() {
			return true // 指针是 nil → 未初始化
		}
		val = val.Elem()
	}

	// 判断最终值是否为零值
	return val.IsZero()
}
