package repo

import (
	"MomentLingo/errs"
	"MomentLingo/model"
	"context"

	"gorm.io/gorm"
)

type vocabularyRepo struct {
	G   gorm.Interface[model.Vocabulary]
	ctx context.Context
}

var VocabularyRepo vocabularyRepo

func (*vocabularyRepo) Clone(db *gorm.DB) *vocabularyRepo {
	return &vocabularyRepo{
		G:   gorm.G[model.Vocabulary](db),
		ctx: context.TODO(),
	}
}

func (it *vocabularyRepo) WithContext(ctx context.Context) {
	it.ctx = ctx
}

func (it *vocabularyRepo) getCtx() context.Context {
	if it.ctx == nil {
		return context.TODO()
	}
	return it.ctx
}

func (it *vocabularyRepo) One(cond model.Vocabulary) model.Vocabulary {
	val, err := it.G.Where(&cond).First(it.getCtx())
	errs.ErrorLogger.SqlQueryError(err)
	return val
}

func (it *vocabularyRepo) AllByIds(ids []int) []model.Vocabulary {
	val, err := it.G.Where("vocabulary_id IN ?", ids).Find(it.getCtx())
	errs.ErrorLogger.SqlQueryError(err)
	return val
}
