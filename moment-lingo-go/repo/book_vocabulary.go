package repo

import (
	"MomentLingo/model"
	"MomentLingo/utils"
	"context"

	"gorm.io/gorm"
)

type bookVocabularyRepo struct {
	G   gorm.Interface[model.BookVocabulary]
	ctx context.Context
}

var BookVocabularyRepo bookVocabularyRepo

func (*bookVocabularyRepo) Clone(db *gorm.DB) *bookVocabularyRepo {
	return &bookVocabularyRepo{
		G:   gorm.G[model.BookVocabulary](db),
		ctx: context.TODO(),
	}
}

func (it *bookVocabularyRepo) WithContext(ctx context.Context) {
	it.ctx = ctx
}

func (it *bookVocabularyRepo) Page(cond model.BookVocabulary, page, size int) utils.PageEntity[model.BookVocabulary] {
	return utils.Paginate(it.G, cond, page, size, utils.PageOpt.WithOrders([]string{"`rank`"}))
}
