package controller

import (
	"MomentLingo/service"
	"MomentLingo/utils"

	"github.com/gin-gonic/gin"
)

type bookController struct {
}

var BookController bookController

func (bookController) ListBooks(c *gin.Context) {
	service.BookService.ListBooks(c)
}

func (bookController) GetBook(c *gin.Context) {
	bookId := utils.Param[int](c, "bookId")
	service.BookService.GetBook(c, bookId)
}

func (bookController) ListBookDetail(c *gin.Context) {
	bookId := utils.Param[int](c, "bookId")
	page := utils.Query[int](c, "page")
	size := utils.Query[int](c, "size")
	service.BookService.ListBookDetail(c, bookId, page, size)
}
