package controller

import (
	"MomentLingo/dto"
	"MomentLingo/service"
	"MomentLingo/utils"

	"github.com/gin-gonic/gin"
)

type authController struct {
}

var AuthController authController

func (authController) SendCaptcha(c *gin.Context) {
	var d dto.CaptchaDto
	utils.ShouldBindJSON(c, &d)
	service.AuthorService.SendCaptcha(c, d)
}

func (authController) Register(c *gin.Context) {
	var d dto.RegisterDto
	utils.ShouldBindJSON(c, &d)
	service.AuthorService.Register(c, d)
}

func (authController) Login(c *gin.Context) {
	var d dto.LoginDto
	utils.ShouldBindJSON(c, &d)
	service.AuthorService.Login(c, d)
}

func (authController) Options(c *gin.Context) {
	service.AuthorService.Options(c)
}
