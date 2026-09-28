package controller

import (
	"MomentLingo/dto"
	"MomentLingo/service"
	"MomentLingo/utils"

	"github.com/gin-gonic/gin"
)

type essayController struct{}

var EssayController essayController

func (essayController) PutEssayCorrectTask(c *gin.Context) {
	var d dto.EssayCorrectDto
	utils.ShouldBindJSON(c, &d)
	service.EssayService.PutEssayCorrectTask(c, d)
}

func (essayController) ListEssayCorrectTask(c *gin.Context) {
	service.EssayService.ListEssayCorrectTask(c)
}

func (essayController) GetEssayCorrectTask(c *gin.Context) {
	taskId := utils.Param[string](c, "taskId")
	service.EssayService.GetEssayCorrectTask(c, taskId)
}

func (essayController) ListEssayCorrect(c *gin.Context) {
	page := utils.Query[int](c, "page")
	size := utils.Query[int](c, "size")
	service.EssayService.ListEssayCorrect(c, page, size)
}

func (essayController) GetEssayCorrect(c *gin.Context) {
	essayId := utils.Param[int64](c, "essayId")
	service.EssayService.GetEssayCorrect(c, essayId)
}
