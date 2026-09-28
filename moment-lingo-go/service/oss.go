package service

import (
	"MomentLingo/dto"
	"MomentLingo/utils"
	"fmt"
	"time"

	"github.com/gin-gonic/gin"
)

type ossService struct {
}

var OssService ossService

func (ossService) GetStsToken(c *gin.Context) {
	utils.Resp.Success(c, utils.RespOpt.WithData(utils.Oss.StsPutToken()))
}

func (ossService) Presign(c *gin.Context, objectName string) {
	utils.Resp.Success(c, utils.RespOpt.WithData(utils.Oss.Presign(objectName)))
}

func (ossService) PutUploadTask(c *gin.Context, d dto.PutUploadTaskDto) {
	if d.TaskId == "" {
		taskId := utils.UUID()
		utils.Rdb.SetEx(fmt.Sprintf("oss:upload:%s", taskId), "WAITING", time.Minute)
		utils.Resp.Success(c, utils.RespOpt.WithData(utils.H{
			"status": "CREATED",
			"taskId": taskId,
		}))
		return
	}

	if d.FileUrl == "" {
		utils.Resp.Error(c, "fileUrl不能为空")
		return
	}

	res := utils.Rdb.Get(fmt.Sprintf("oss:upload:%s", d.TaskId))
	if res == nil {
		utils.Resp.Success(c, utils.RespOpt.WithData(utils.H{
			"status": "FAILED",
			"error":  "任务不存在",
		}))
		return
	}

	utils.Rdb.SetEx(fmt.Sprintf("oss:upload:%s", d.TaskId), d.FileUrl, time.Minute)
	utils.Resp.Success(c)
}

func (ossService) GetUploadTask(c *gin.Context, taskId string) {
	res := utils.Rdb.Get(fmt.Sprintf("oss:upload:%s", taskId))
	if res == nil {
		utils.Resp.Success(c, utils.RespOpt.WithData(utils.H{
			"status": "FAILED",
			"error":  "任务不存在",
		}))
		return
	}

	if *res == "WAITING" {
		utils.Resp.Success(c, utils.RespOpt.WithData(utils.H{
			"status": "WAITING",
		}))
		return
	}

	utils.Rdb.Del(fmt.Sprintf("oss:upload:%s", taskId))
	utils.Resp.Success(c, utils.RespOpt.WithData(utils.H{
		"status":  "SUCCEED",
		"fileUrl": *res,
	}))
}
