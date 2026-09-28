package controller

import (
	"MomentLingo/dto"
	"MomentLingo/service"
	"MomentLingo/utils"

	"github.com/gin-gonic/gin"
)

type userController struct {
}

var UserController userController

func (userController) GetUser(c *gin.Context) {
	service.UserService.GetUser(c)
}

func (userController) PatchUser(c *gin.Context) {
	var d dto.PatchUserDto
	utils.ShouldBindJSON(c, &d)
	service.UserService.PatchUser(c, d)
}
