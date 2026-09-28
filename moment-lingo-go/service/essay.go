package service

import (
	"MomentLingo/config"
	"MomentLingo/dto"
	"MomentLingo/model"
	"MomentLingo/repo"
	"MomentLingo/utils"
	"fmt"
	"sort"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/go-resty/resty/v2"
)

type essayService struct{}

var EssayService essayService

func (essayService) PutEssayCorrectTask(c *gin.Context, d dto.EssayCorrectDto) {
	userId := utils.GetUserId(c)
	client := resty.New()

	r, err := client.R().SetBody(utils.H{
		"userId":  userId,
		"content": d.Content,
	}).Post(fmt.Sprintf("%s/essay/correct/task", config.Conf.Python.Url))

	resp := utils.Resp.BuildWithRestyResp(r)
	if err != nil || resp.Code != 200 {
		utils.Resp.Error(c, "参数错误", utils.RespOpt.WithCode(422))
		return
	}

	resp.Return(c)
}

func (essayService) ListEssayCorrectTask(c *gin.Context) {
	userId := utils.GetUserId(c)
	keys := utils.Rdb.Scan(fmt.Sprintf("essay:correct:%d:*", userId))

	res := make([]map[string]string, 0)
	for _, key := range keys {
		res = append(res, utils.Rdb.HGetAll(key))
	}

	// 降序排列
	sort.Slice(res, func(i, j int) bool {
		timeI, _ := time.Parse(time.DateTime, res[i]["createdAt"])
		timeJ, _ := time.Parse(time.DateTime, res[j]["createdAt"])
		return timeI.After(timeJ)
	})

	utils.Resp.Success(c, utils.RespOpt.WithData(res))
}

func (essayService) GetEssayCorrectTask(c *gin.Context, taskId string) {
	userId := utils.GetUserId(c)
	res := utils.Rdb.HGetAll(fmt.Sprintf("essay:correct:%d:%s", userId, taskId))
	utils.Resp.Success(c, utils.RespOpt.WithData(res))
}

func (essayService) ListEssayCorrect(c *gin.Context, page, size int) {
	userId := utils.GetUserId(c)
	res := repo.EssayRepo.Page(model.Essay{
		UserId: new(userId),
	}, page, size)

	utils.Resp.Success(c, utils.RespOpt.WithData(res))
}

func (essayService) GetEssayCorrect(c *gin.Context, essayId int64) {
	userId := utils.GetUserId(c)
	res := repo.EssayRepo.One(model.Essay{
		EssayId: new(essayId),
		UserId:  new(userId),
	})

	if utils.IsZero(res) {
		utils.Resp.Error(c, "作文不存在")
		return
	}

	utils.Resp.Success(c, utils.RespOpt.WithData(res))
}
