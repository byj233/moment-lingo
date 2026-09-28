package repo

import (
	"MomentLingo/errs"
	"MomentLingo/model"
	"context"

	"gorm.io/gorm"
)

type bookRepo struct {
	G   gorm.Interface[model.Book]
	ctx context.Context
}

var BookRepo bookRepo

func (*bookRepo) Clone(db *gorm.DB) *bookRepo {
	return &bookRepo{
		G:   gorm.G[model.Book](db),
		ctx: context.TODO(),
	}
}

func (it *bookRepo) WithContext(ctx context.Context) {
	it.ctx = ctx
}

func (it *bookRepo) getCtx() context.Context {
	if it.ctx == nil {
		return context.TODO()
	}
	return it.ctx
}

func (it *bookRepo) One(cond model.Book) model.Book {
	val, err := it.G.Where(&cond).First(it.getCtx())
	errs.ErrorLogger.SqlQueryError(err)
	return val
}

func (it *bookRepo) All(cond model.Book) []model.Book {
	val, err := it.G.Where(&cond).Find(it.getCtx())
	errs.ErrorLogger.SqlQueryError(err)
	return val
}
