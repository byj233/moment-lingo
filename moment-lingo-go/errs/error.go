package errs

import (
	"errors"
	"fmt"
	"log/slog"

	"gorm.io/gorm"
)

type CustomError struct {
	Code int
	Msg  string
}

func (e *CustomError) Error() string {
	return fmt.Sprintf("[%d] %s", e.Code, e.Msg)
}

type errorLogger struct{}

var ErrorLogger errorLogger

func (errorLogger) SqlInsertError(err error) {
	if err == nil {
		return
	}

	slog.Error("数据库插入错误", "SqlInsertError", err)
	panic(fmt.Errorf("数据库插入错误 %w", err))
}

func (errorLogger) SqlUpdateError(err error) {
	if err == nil {
		return
	}

	slog.Error("数据库更新错误", "SqlUpdateError", err)
	panic(fmt.Errorf("数据库插入错误 %w", err))
}

func (errorLogger) SqlQueryError(err error) {
	if err == nil || errors.Is(err, gorm.ErrRecordNotFound) {
		return
	}

	slog.Error("数据库查询错误", "SqlQueryError", err)
	panic(fmt.Errorf("数据库插入错误 %w", err))
}

func (errorLogger) SqlDeleteError(err error) {
	if err == nil {
		return
	}

	slog.Error("数据库删除错误", "SqlDeleteError", err)
	panic(fmt.Errorf("数据库插入错误 %w", err))
}

func (errorLogger) SqlUpsertError(err error) {
	if err == nil {
		return
	}

	slog.Error("数据库插入或更新错误", "SqlUpsertError", err)
	panic(fmt.Errorf("数据库插入错误 %w", err))
}
