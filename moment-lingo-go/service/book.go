package service

import (
	"MomentLingo/model"
	"MomentLingo/repo"
	"MomentLingo/utils"

	"github.com/gin-gonic/gin"
)

type bookService struct {
}

var BookService bookService

func (bookService) ListBooks(c *gin.Context) {
	res := repo.BookRepo.All(model.Book{})
	utils.Resp.Success(c, utils.RespOpt.WithData(res))
}

func (bookService) GetBook(c *gin.Context, bookId int) {
	res := repo.BookRepo.One(model.Book{BookId: new(bookId)})
	if utils.IsZero(res) {
		utils.Resp.Error(c, "词书不存在")
		return
	}
	utils.Resp.Success(c, utils.RespOpt.WithData(res))
}

func (bookService) ListBookDetail(c *gin.Context, bookId, page, size int) {
	book := repo.BookRepo.One(model.Book{BookId: new(bookId)})
	if utils.IsZero(book) {
		utils.Resp.Error(c, "词书不存在")
		return
	}

	bookDetail := repo.BookVocabularyRepo.Page(model.BookVocabulary{BookId: new(bookId)}, page, size)
	vocabularyIds := make([]int, 0)

	for _, item := range bookDetail.Data {
		vocabularyIds = append(vocabularyIds, *item.VocabularyId)
	}

	vocabulary := repo.VocabularyRepo.AllByIds(vocabularyIds)
	data := utils.JSON.ToArray(vocabulary)
	for index, item := range data {
		mp, _ := item.(map[string]any)
		mp["rank"] = bookDetail.Data[index].Rank
	}

	utils.Resp.Success(c, utils.RespOpt.WithData(utils.PageEntity[any]{
		Total:   bookDetail.Total,
		Pages:   bookDetail.Pages,
		Current: bookDetail.Current,
		Data:    data,
	}))
}
