package service

import (
	"MomentLingo/dto"
	"MomentLingo/model"
	"MomentLingo/repo"
	"MomentLingo/utils"
	"strings"

	"github.com/gin-gonic/gin"
)

type userService struct {
}

var UserService userService

func (userService) GetUser(c *gin.Context) {
	userId := utils.GetUserId(c)
	user := repo.UserRepo.One(model.User{
		UserId: new(userId),
	})

	utils.Resp.Success(c, utils.RespOpt.WithData(utils.H{
		"userId":    user.UserId,
		"nickname":  user.Nickname,
		"avatarUrl": utils.Oss.BuildUrl(*user.AvatarUrl),
	}))
}

func (userService) PatchUser(c *gin.Context, d dto.PatchUserDto) {
	userId := utils.GetUserId(c)

	if d.Nickname == nil && d.AvatarUrl == nil {
		utils.Resp.Success(c)
		return
	}

	var updateData model.User

	if d.Nickname != nil {
		nickname := strings.TrimSpace(*d.Nickname)
		if nickname == "" {
			utils.Resp.Error(c, "昵称不能为空")
			return
		}

		if len(nickname) > 20 {
			utils.Resp.Error(c, "昵称不能超过20个字符")
			return
		}
		updateData.Nickname = &nickname
	}

	if d.AvatarUrl != nil {
		avatarUrl := strings.TrimSpace(*d.AvatarUrl)
		if avatarUrl == "" {
			utils.Resp.Error(c, "头像不能为空")
			return
		}
		updateData.AvatarUrl = &avatarUrl
		utils.Oss.PublicReadAcl(avatarUrl)
	}

	repo.UserRepo.UpdateById(userId, updateData)
	utils.Resp.Success(c)
}
