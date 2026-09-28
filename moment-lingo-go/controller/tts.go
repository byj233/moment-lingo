package controller

import (
	"MomentLingo/dto"
	"MomentLingo/service"
	"MomentLingo/utils"

	"github.com/gin-gonic/gin"
)

type ttsController struct {
}

var TtsController ttsController

func (ttsController) TtsStream(c *gin.Context) {
	var d dto.TtsDto
	utils.ShouldBindJSON(c, &d)
	service.TtsService.TtsStream(c, d)
}

func (ttsController) ListVoices(c *gin.Context) {
	service.TtsService.ListVoices(c)
}
