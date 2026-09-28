package controller

import (
	"MomentLingo/dto"
	"MomentLingo/service"
	"MomentLingo/utils"

	"github.com/gin-gonic/gin"
)

type ossController struct {
}

var OssController ossController

func (ossController) GetStsToken(c *gin.Context) {
	service.OssService.GetStsToken(c)
}

func (ossController) Presign(c *gin.Context) {
	objectName := utils.Query[string](c, "objectName")
	service.OssService.Presign(c, objectName)
}

func (ossController) PutUploadTask(c *gin.Context) {
	var d dto.PutUploadTaskDto
	utils.ShouldBindJSON(c, &d)
	service.OssService.PutUploadTask(c, d)
}

func (ossController) GetUploadTask(c *gin.Context) {
	taskId := utils.Param[string](c, "taskId")
	service.OssService.GetUploadTask(c, taskId)
}
