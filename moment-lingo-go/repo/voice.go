package repo

import (
	"MomentLingo/errs"
	"MomentLingo/model"
	"context"

	"gorm.io/gorm"
)

type voiceRepo struct {
	G   gorm.Interface[model.Voice]
	ctx context.Context
}

var VoiceRepo voiceRepo

func (*voiceRepo) Clone(db *gorm.DB) *voiceRepo {
	return &voiceRepo{
		G:   gorm.G[model.Voice](db),
		ctx: context.TODO(),
	}
}

func (it *voiceRepo) WithContext(ctx context.Context) {
	it.ctx = ctx
}

func (it *voiceRepo) getCtx() context.Context {
	if it.ctx == nil {
		return context.TODO()
	}
	return it.ctx
}

func (it *voiceRepo) All(cond model.Voice) []model.Voice {
	val, err := it.G.Where(&cond).Order("weight DESC").Find(it.getCtx())
	errs.ErrorLogger.SqlQueryError(err)
	return val
}
