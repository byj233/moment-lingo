package repo

import (
	"MomentLingo/errs"
	"MomentLingo/model"
	"context"

	"gorm.io/gorm"
)

type userRepo struct {
	G   gorm.Interface[model.User]
	ctx context.Context
}

var UserRepo userRepo

func (*userRepo) Clone(db *gorm.DB) *userRepo {
	return &userRepo{
		G:   gorm.G[model.User](db),
		ctx: context.TODO(),
	}
}

func (it *userRepo) WithContext(ctx context.Context) {
	it.ctx = ctx
}

func (it *userRepo) getCtx() context.Context {
	if it.ctx == nil {
		return context.TODO()
	}
	return it.ctx
}

func (it *userRepo) Create(item model.User) {
	err := it.G.Create(it.getCtx(), &item)
	if err != nil {
		errs.ErrorLogger.SqlInsertError(err)
	}
}

func (it *userRepo) UpdateById(userId int64, item model.User) {
	_, err := it.G.Where("user_id = ?", userId).Updates(it.getCtx(), item)
	if err != nil {
		errs.ErrorLogger.SqlUpdateError(err)
	}
}

func (it *userRepo) One(cond model.User) model.User {
	val, err := it.G.Where(&cond).First(it.getCtx())
	errs.ErrorLogger.SqlQueryError(err)
	return val
}
