package utils

import (
	"encoding/json"
	"fmt"
	"log/slog"

	"gorm.io/datatypes"
	"gorm.io/gorm"
)

type jsonUtil struct {
}

var JSON jsonUtil

func (jsonUtil) panicErr(err error) {
	slog.Error("json异常", "JsonError", err)
	panic(fmt.Errorf("json异常 %w", err))
}

func (jsonUtil) StrToArray(jsonStr string) (arr []any) {
	if err := json.Unmarshal([]byte(jsonStr), &arr); err != nil {
		JSON.panicErr(err)
	}
	return
}

func (jsonUtil) StrToMap(jsonStr string) (mp map[string]any) {
	if err := json.Unmarshal([]byte(jsonStr), &mp); err != nil {
		JSON.panicErr(err)
	}
	return
}

func (jsonUtil) Stringify(data any) string {
	b, err := json.Marshal(data)
	if err != nil {
		JSON.panicErr(err)
	}
	return string(b)
}

func (jsonUtil) ToJson(data any) datatypes.JSON {
	b, err := json.Marshal(data)
	if err != nil {
		JSON.panicErr(err)
	}
	return b
}

func (jsonUtil) ToArray(data any) (arr []any) {
	if str, ok := data.(string); ok {
		return JSON.StrToArray(str)
	}
	str := JSON.Stringify(data)
	arr = JSON.StrToArray(str)
	return
}

func (jsonUtil) ToMap(data any) (mp map[string]any) {
	if str, ok := data.(string); ok {
		return JSON.StrToMap(str)
	}
	str := JSON.Stringify(data)
	mp = JSON.StrToMap(str)
	return
}

// JsonContainsAll 查询json数组字段是否包含所有指定的标签
func (jsonUtil) JsonContainsAll(column string, json datatypes.JSON) func(*gorm.Statement) {
	arr := JSON.ToArray(json)
	return func(db *gorm.Statement) {
		for _, item := range arr {
			db.Where(datatypes.JSONArrayQuery(column).Contains(item))
		}

	}
}
