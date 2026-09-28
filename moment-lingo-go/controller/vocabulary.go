package controller

import (
	"MomentLingo/service"
	"MomentLingo/utils"

	"github.com/gin-gonic/gin"
)

type vocabularyController struct {
}

var VocabularyController vocabularyController

func (vocabularyController) GetDetailVocabulary(c *gin.Context) {
	id := utils.Param[int](c, "vocabularyId")
	service.VocabularyService.GetDetailVocabulary(c, id)
}

func (vocabularyController) GetBriefVocabulary(c *gin.Context) {
	id := utils.Param[int](c, "vocabularyId")
	service.VocabularyService.GetBriefVocabulary(c, id)
}

func (vocabularyController) GetVocabulary(c *gin.Context) {
	vocabulary := utils.Param[string](c, "vocabulary")
	service.VocabularyService.GetVocabulary(c, vocabulary)
}
