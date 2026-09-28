package controller

import (
	"MomentLingo/dto"
	"MomentLingo/service"
	"MomentLingo/utils"

	"github.com/gin-gonic/gin"
)

type searchController struct {
}

var SearchController searchController

func (searchController) SearchVocabulary(c *gin.Context) {
	var d dto.SearchVocabularyDto
	utils.ShouldBindJSON(c, &d)
	service.SearchService.SearchVocabulary(c, d)
}
