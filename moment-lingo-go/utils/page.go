package utils

import (
	"MomentLingo/errs"
	"context"

	"gorm.io/gorm"
)

type PageEntity[T any] struct {
	Total   int `json:"total"`
	Pages   int `json:"pages"`
	Current int `json:"current"`
	Data    []T `json:"data"`
}

type paginateOption func(*paginateOptions)

type paginateOptions struct {
	orders []string
}

type paginateOptionUtil struct{}

var PageOpt paginateOptionUtil

func (p paginateOptionUtil) WithOrders(orders []string) paginateOption {
	return func(o *paginateOptions) {
		o.orders = append(o.orders, orders...)
	}
}

func Paginate[T any](g gorm.Interface[T], cond T, page, size int, opts ...paginateOption) PageEntity[T] {
	if page < 1 {
		page = 1
	}
	if size < 1 {
		size = 10
	}
	if size > 100 {
		size = 100
	}

	opt := &paginateOptions{}
	for _, f := range opts {
		f(opt)
	}

	total, err := g.Where(&cond).Count(context.TODO(), "*")
	errs.ErrorLogger.SqlQueryError(err)

	query := g.Where(&cond)
	for _, order := range opt.orders {
		query = query.Order(order)
	}

	val, err := query.Limit(size).Offset((page - 1) * size).Find(context.TODO())
	errs.ErrorLogger.SqlQueryError(err)
	return PageEntity[T]{
		Total:   int(total),
		Pages:   (int(total) + size - 1) / size,
		Current: page,
		Data:    val,
	}
}
