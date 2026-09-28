package service

import (
	"MomentLingo/config"
	"MomentLingo/dto"
	"MomentLingo/utils"
	"fmt"

	"github.com/gin-gonic/gin"
	"github.com/go-resty/resty/v2"
)

type aiService struct {
}

var AIService aiService

func (aiService) OCR(c *gin.Context, d dto.OCRDto) {
	utils.SSE.New().
		SetUrl(fmt.Sprintf("%s/ai/ocr", config.Conf.Python.Url)).
		SetMethod("POST").
		SetBody(utils.JSON.ToMap(d)).
		Stream(c)
}

func (aiService) ExtensionTranslate(c *gin.Context, d dto.ExtensionTranslateDto) {
	utils.SSE.New().
		SetUrl(fmt.Sprintf("%s/ai/extension/translate", config.Conf.Python.Url)).
		SetMethod("POST").
		SetBody(utils.JSON.ToMap(d)).
		Stream(c)
}

func (aiService) AIWrite(c *gin.Context, d dto.AIWriteDto) {
	client := resty.New()
	r, err := client.R().SetBody(d).Post(fmt.Sprintf("%s/ai/write", config.Conf.Python.Url))

	resp := utils.Resp.BuildWithRestyResp(r)
	if err != nil || resp.Code != 200 {
		utils.Resp.Error(c, "参数错误", utils.RespOpt.WithCode(422))
		return
	}

	resp.Return(c)
}
