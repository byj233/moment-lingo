package repo

import (
	"MomentLingo/errs"
	"MomentLingo/model"
	"context"

	"gorm.io/gorm"
)

type phraseRepo struct {
	G   gorm.Interface[model.Phrase]
	ctx context.Context
}

var PhraseRepo phraseRepo

func (*phraseRepo) Clone(db *gorm.DB) *phraseRepo {
	return &phraseRepo{
		G:   gorm.G[model.Phrase](db),
		ctx: context.TODO(),
	}
}

func (it *phraseRepo) WithContext(ctx context.Context) {
	it.ctx = ctx
}

func (it *phraseRepo) getCtx() context.Context {
	if it.ctx == nil {
		return context.TODO()
	}
	return it.ctx
}

func (it *phraseRepo) One(cond model.Phrase) model.Phrase {
	val, err := it.G.Where(&cond).First(it.getCtx())
	errs.ErrorLogger.SqlQueryError(err)
	return val
}

func (it *phraseRepo) AllByIds(ids []int) []model.Phrase {
	val, err := it.G.Where("phrase_id IN ?", ids).Find(it.getCtx())
	errs.ErrorLogger.SqlQueryError(err)
	return val
}
