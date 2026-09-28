package repo

import (
	"MomentLingo/errs"
	"MomentLingo/model"
	"context"

	"gorm.io/gorm"
)

type wordRepo struct {
	G   gorm.Interface[model.Word]
	ctx context.Context
}

var WordRepo wordRepo

func (*wordRepo) Clone(db *gorm.DB) *wordRepo {
	return &wordRepo{
		G:   gorm.G[model.Word](db),
		ctx: context.TODO(),
	}
}

func (it *wordRepo) WithContext(ctx context.Context) {
	it.ctx = ctx
}

func (it *wordRepo) getCtx() context.Context {
	if it.ctx == nil {
		return context.TODO()
	}
	return it.ctx
}

func (it *wordRepo) One(cond model.Word) model.Word {
	val, err := it.G.Where(&cond).First(it.getCtx())
	errs.ErrorLogger.SqlQueryError(err)
	return val
}

func (it *wordRepo) AllByIds(ids []int) []model.Word {
	val, err := it.G.Where("word_id IN ?", ids).Find(it.getCtx())
	errs.ErrorLogger.SqlQueryError(err)
	return val
}
