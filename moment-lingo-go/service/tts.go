package service

import (
	"MomentLingo/config"
	"MomentLingo/dto"
	"MomentLingo/model"
	"MomentLingo/repo"
	"MomentLingo/utils"
	"fmt"

	"github.com/gin-gonic/gin"
)

type ttsService struct {
}

var TtsService ttsService

func (ttsService) TtsStream(c *gin.Context, d dto.TtsDto) {
	utils.SSE.New().
		SetUrl(fmt.Sprintf("%s/tts", config.Conf.Python.Url)).
		SetMethod("POST").
		SetBody(utils.JSON.ToMap(d)).
		Stream(c)
}

func (ttsService) ListVoices(c *gin.Context) {
	voices := repo.VoiceRepo.All(model.Voice{})
	utils.Resp.Success(c, utils.RespOpt.WithData(voices))
}
