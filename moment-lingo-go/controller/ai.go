package controller

import (
	"MomentLingo/dto"
	"MomentLingo/service"
	"MomentLingo/utils"

	"github.com/gin-gonic/gin"
)

type aiController struct {
}

var AIController aiController

func (aiController) OCR(c *gin.Context) {
	var d dto.OCRDto
	utils.ShouldBindJSON(c, &d)
	service.AIService.OCR(c, d)
}

func (aiController) ExtensionTranslate(c *gin.Context) {
	var d dto.ExtensionTranslateDto
	utils.ShouldBindJSON(c, &d)
	service.AIService.ExtensionTranslate(c, d)
}

func (aiController) AIWrite(c *gin.Context) {
	var d dto.AIWriteDto
	utils.ShouldBindJSON(c, &d)
	service.AIService.AIWrite(c, d)
}
