package repo

import (
	"MomentLingo/errs"
	"MomentLingo/model"
	"MomentLingo/utils"
	"context"

	"gorm.io/gorm"
)

type essayRepo struct {
	G   gorm.Interface[model.Essay]
	ctx context.Context
}

var EssayRepo essayRepo

func (*essayRepo) Clone(db *gorm.DB) *essayRepo {
	return &essayRepo{
		G:   gorm.G[model.Essay](db),
		ctx: context.TODO(),
	}
}

func (it *essayRepo) WithContext(ctx context.Context) {
	it.ctx = ctx
}

func (it *essayRepo) GetCtx() context.Context {
	if it.ctx == nil {
		return context.TODO()
	}
	return it.ctx
}

func (it *essayRepo) One(cond model.Essay) model.Essay {
	val, err := it.G.Where(&cond).First(it.GetCtx())
	errs.ErrorLogger.SqlQueryError(err)
	return val
}
func (it *essayRepo) Page(cond model.Essay, page, size int) utils.PageEntity[model.Essay] {
	return utils.Paginate(it.G, cond, page, size, utils.PageOpt.WithOrders([]string{"created_at DESC"}))
}
