package utils

import (
	"MomentLingo/config"
	"bytes"
	"encoding/json"
	"fmt"
	"log/slog"
	"net/http"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/go-resty/resty/v2"
)

type Response struct {
	Code      int    `json:"code"`
	Msg       string `json:"msg"`
	Data      any    `json:"data"`
	Timestamp int64  `json:"timestamp"`
}

type respOption func(*Response)

type respOptionUtil struct{}

var RespOpt respOptionUtil

type respUtil struct{}

var Resp respUtil

func (r respOptionUtil) WithMsg(msg string) respOption {
	return func(o *Response) {
		o.Msg = msg
	}
}

func (r respOptionUtil) WithCode(code int) respOption {
	return func(o *Response) {
		o.Code = code
	}
}

func (r respOptionUtil) WithData(data any) respOption {
	return func(o *Response) {
		o.Data = formatDataForInt64(data)
	}
}

func (r respUtil) Success(c *gin.Context, opts ...respOption) {
	resp := &Response{
		Msg:       "成功",
		Code:      200,
		Timestamp: Timestamp(),
	}

	for _, opt := range opts {
		opt(resp)
	}

	c.JSON(http.StatusOK, resp)
}

func (r respUtil) Error(c *gin.Context, msg string, opts ...respOption) {
	resp := &Response{
		Msg:  msg,
		Code: 500,
	}
	for _, opt := range opts {
		opt(resp)
	}

	c.JSON(http.StatusOK, resp)
}

func (respUtil) BuildWithRestyResp(resp *resty.Response) Response {
	if resp.StatusCode() != 200 {
		url := strings.Replace(resp.Request.URL, config.Conf.Python.Url, "", 1)
		slog.Error(fmt.Sprintf("调用外部服务失败 URL: %s", url))
		panic(fmt.Errorf("调用外部服务失败 URL: %s", url))
	}
	return byteToObject[Response](resp.Body())
}

func (r respUtil) StreamError(c *gin.Context, opts ...respOption) {
	options := &Response{
		Msg:  "internal server error",
		Code: 500,
	}
	for _, opt := range opts {
		opt(options)
	}

	c.SSEvent("ERROR", Response{
		Code:      options.Code,
		Msg:       options.Msg,
		Data:      options.Data,
		Timestamp: Timestamp(),
	})
	c.Writer.Flush()
}

// Return 返回响应 调用外部服务时使用 直接返回响应体
func (r *Response) Return(c *gin.Context) {
	c.JSON(http.StatusOK, r)
}

func byteToObject[T any](b []byte) T {
	var res T
	err := json.Unmarshal(b, &res)
	if err != nil {
		JSON.panicErr(err)
	}
	return res
}

func formatDataForInt64(data any) any {
	if data == nil {
		return nil
	}

	// 快速处理基本类型
	switch v := data.(type) {
	case int64:
		return strconv.FormatInt(v, 10)
	case uint64:
		return strconv.FormatUint(v, 10)
	}

	// 通过 JSON 序列化和反序列化处理嵌套的 long int
	// 这样可以保留 time.Time 和自定义 MarshalJSON 的结果
	b, err := json.Marshal(data)
	if err != nil {
		return data
	}

	decoder := json.NewDecoder(bytes.NewReader(b))
	decoder.UseNumber()
	var decodedData any
	err = decoder.Decode(&decodedData)
	if err != nil {
		return data
	}

	return processDecodedNumber(decodedData)
}

const (
	maxSafeInteger = 1<<53 - 1
	minSafeInteger = -maxSafeInteger
)

func processDecodedNumber(v any) any {
	switch val := v.(type) {
	case map[string]any:
		for k, mapVal := range val {
			val[k] = processDecodedNumber(mapVal)
		}
		return val
	case []any:
		for i, sliceVal := range val {
			val[i] = processDecodedNumber(sliceVal)
		}
		return val
	case json.Number:
		if strings.Contains(val.String(), ".") {
			f, _ := val.Float64()
			return f
		}
		i, err := val.Int64()
		if err == nil {
			// 如果超出 JavaScript 安全整数范围 (2^53 - 1)，则转换为字符串
			// 否则前端可能会丢失精度
			if i > maxSafeInteger || i < minSafeInteger {
				return val.String()
			}
			return i
		}
		// 尝试 uint64
		if u, err := strconv.ParseUint(val.String(), 10, 64); err == nil {
			if u > maxSafeInteger {
				return val.String()
			}
			return u
		}
		return val.String()
	default:
		return v
	}
}
