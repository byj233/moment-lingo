package service

import (
	"MomentLingo/model"
	"MomentLingo/repo"
	"MomentLingo/utils"

	"github.com/gin-gonic/gin"
)

type vocabularyService struct {
}

var VocabularyService vocabularyService

func (vocabularyService) GetDetailVocabulary(c *gin.Context, vocabularyId int) {
	vocabulary := repo.VocabularyRepo.One(model.Vocabulary{
		VocabularyId: new(vocabularyId),
	})

	if utils.IsZero(vocabulary) {
		utils.Resp.Error(c, "词汇不存在")
		return
	}

	// 无类型模式
	if vocabulary.Type == nil {
		utils.Resp.Success(c, utils.RespOpt.WithData(vocabulary))
		return
	}

	// 单词模式
	if "word" == *vocabulary.Type {
		word := repo.WordRepo.One(model.Word{WordId: vocabulary.LexicalId})

		res := utils.JSON.ToMap(word)
		res["vocabulary"] = vocabulary
		utils.Resp.Success(c, utils.RespOpt.WithData(res))
		return
	}

	// 短语模式
	if "phrase" == *vocabulary.Type {
		phrase := repo.PhraseRepo.One(model.Phrase{PhraseId: vocabulary.LexicalId})

		res := utils.JSON.ToMap(phrase)
		res["vocabulary"] = vocabulary
		utils.Resp.Success(c, utils.RespOpt.WithData(res))
		return
	}

}

func (vocabularyService) GetBriefVocabulary(c *gin.Context, vocabularyId int) {
	res := repo.VocabularyRepo.One(model.Vocabulary{
		VocabularyId: new(vocabularyId),
	})

	if utils.IsZero(res) {
		utils.Resp.Error(c, "词汇不存在")
		return
	}

	utils.Resp.Success(c, utils.RespOpt.WithData(res))
}

func (vocabularyService) GetVocabulary(c *gin.Context, vocabulary string) {
	res := repo.VocabularyRepo.One(model.Vocabulary{
		Vocabulary: new(vocabulary),
	})

	if utils.IsZero(res) {
		utils.Resp.Error(c, "词汇不存在")
		return
	}

	utils.Resp.Success(c, utils.RespOpt.WithData(res))
}
