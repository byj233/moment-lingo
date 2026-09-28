package service

import (
	"MomentLingo/dto"
	"MomentLingo/model"
	"MomentLingo/repo"
	"MomentLingo/utils"
	"fmt"
	"math/rand"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

type authService struct {
}

var AuthorService authService

func (authService) Register(c *gin.Context, d dto.RegisterDto) {
	at := getAccountType(d.Account)
	if at == -1 {
		utils.Resp.Error(c, "账号格式错误 非正确的手机格式或邮箱格式")
		return
	}

	register(c, d, at)
}

func (authService) SendCaptcha(c *gin.Context, d dto.CaptchaDto) {
	at := getAccountType(d.Account)
	if at == -1 {
		utils.Resp.Error(c, "账号格式错误 非正确的手机格式或邮箱格式")
		return
	}

	sendCaptcha(c, d, at)
}

func (authService) Login(c *gin.Context, d dto.LoginDto) {
	at := getAccountType(d.Account)
	if at == -1 {
		utils.Resp.Error(c, "账号格式错误 非正确的手机格式或邮箱格式")
		return
	}

	login(c, d, at)
}

func (authService) Options(c *gin.Context) {
	utils.Resp.Success(c)
}

func getAccountType(account string) int {
	if utils.IsValidEmail(account) {
		return 1
	}

	if utils.IsValidPhone(account) {
		return 2
	}

	return -1
}

// 缓存验证码
func cacheCaptcha(c *gin.Context, key, captcha string) bool {
	tryKey := fmt.Sprintf("try:%s", key)
	tryVal := utils.Rdb.Get(tryKey)

	// 首次发送验证码
	if tryVal == nil {
		utils.Rdb.SetEx(tryKey, 1, time.Minute*10)
		utils.Rdb.SetEx(key, captcha, time.Minute*5)
		return true
	}

	if utils.StrToInt[int](*tryVal) >= 3 {
		utils.Resp.Error(c, "验证码发送次数已达上限，请过段时间再试")
		return false
	}

	utils.Rdb.SetEx(tryKey, utils.StrToInt[int](*tryVal)+1, time.Minute*10)
	utils.Rdb.SetEx(key, captcha, time.Minute*5)
	return true
}

func sendCaptcha(c *gin.Context, d dto.CaptchaDto, at int) {
	if at == 1 {
		sendCaptchaToEmail(c, d)
	} else {
		sendCaptchaToPhone(c, d)
	}
}

func sendCaptchaToEmail(c *gin.Context, d dto.CaptchaDto) {
	key := fmt.Sprintf("%s:%s", d.Scene, d.Account)
	code := randomCode(6)

	if !cacheCaptcha(c, key, code) {
		return
	}

	utils.SendCaptchaEmail(d.Account, code)
	utils.Resp.Success(c)
}

func sendCaptchaToPhone(c *gin.Context, d dto.CaptchaDto) {
	key := fmt.Sprintf("%s:%s", d.Scene, d.Account)
	captcha := randomCode(6)

	if !cacheCaptcha(c, key, captcha) {
		return
	}

	utils.SendCaptchaMessage(d.Account, captcha)
	utils.Resp.Success(c)
}

func randomCode(limit int) string {
	r := rand.New(rand.NewSource(time.Now().UnixNano()))
	const digits = "0123456789"

	result := make([]byte, limit)
	for i := 0; i < limit; i++ {
		result[i] = digits[r.Intn(10)]
	}

	return string(result)
}

// 检查错误和用户是否存在
func checkUser(account string, at int) (hasUser bool, user model.User) {
	if at == 1 {
		user := repo.UserRepo.One(model.User{
			Email: &account,
		})

		if (user != model.User{}) {
			return true, user
		}
	} else {
		user := repo.UserRepo.One(model.User{
			Phone: &account,
		})

		if (user != model.User{}) {
			return true, user
		}
	}

	return false, user
}

// 检查验证码是否存在 是否正确
func checkCaptcha(c *gin.Context, key, captcha string) bool {
	val := utils.Rdb.Get(key)
	// 验证码不存在
	if val == nil {
		utils.Resp.Error(c, "未发送验证码")
		return false
	}

	if *val != captcha {
		utils.Resp.Error(c, "验证码错误")
		return false
	}

	utils.Rdb.Del(key)
	return true
}

// keyPrefix 用于校验直接注册 或 首次sms登录注册
func register(c *gin.Context, d dto.RegisterDto, at int) {
	hasUser, _ := checkUser(d.Account, at)

	// 用户已存在
	if hasUser {
		utils.Resp.Error(c, "注册时账户已存在")
		return
	}

	// 密码校验
	if !utils.ValidatePasscode(d.Passcode) {
		utils.Resp.Error(c, "密码格式错误")
		return
	}

	key := fmt.Sprintf("register:%s", d.Account)
	if !checkCaptcha(c, key, d.Captcha) {
		return
	}

	// 密码加密
	encrypt := utils.Encrypt(d.Passcode)
	userId := utils.GenerateSnowflakeId()

	if at == 1 {
		repo.UserRepo.Create(model.User{
			UserId:   &userId,
			Nickname: &d.Nickname,
			Passcode: &encrypt,
			Email:    &d.Account,
		})
	} else {
		repo.UserRepo.Create(model.User{
			UserId:   &userId,
			Nickname: &d.Nickname,
			Passcode: &encrypt,
			Phone:    &d.Account,
		})
	}

	utils.Resp.Success(c, utils.RespOpt.WithData(utils.H{
		"userId":    &userId,
		"nickname":  &d.Nickname,
		"avatarUrl": utils.Oss.BuildUrl("default-avatar.webp"),
		"token":     utils.TokenManager.Add(userId),
	}))
}

func login(c *gin.Context, d dto.LoginDto, at int) {
	if d.Scene == "pwd" {
		loginByPwd(c, d, at)
	} else {
		loginBySms(c, d, at)
	}
}

func loginByPwd(c *gin.Context, d dto.LoginDto, at int) {
	if d.Passcode == nil || strings.TrimSpace(*d.Passcode) == "" {
		utils.Resp.Error(c, "密码不能为空")
		return
	}

	hasUser, user := checkUser(d.Account, at)

	if !hasUser {
		utils.Resp.Error(c, "用户不存在")
		return
	}

	if user.Passcode == nil {
		utils.Resp.Error(c, "该账号未设置密码")
		return
	}

	if !utils.CompareCrypt(*user.Passcode, *d.Passcode) {
		utils.Resp.Error(c, "密码错误")
		return
	}

	utils.Resp.Success(c, utils.RespOpt.WithData(utils.H{
		"userId":    user.UserId,
		"nickname":  user.Nickname,
		"avatarUrl": utils.Oss.BuildUrl(*user.AvatarUrl),
		"token":     utils.TokenManager.Add(*user.UserId),
	}))
}

func loginBySms(c *gin.Context, d dto.LoginDto, at int) {
	if d.Captcha == nil || strings.TrimSpace(*d.Captcha) == "" {
		utils.Resp.Error(c, "验证码不能为空")
		return
	}

	hasUser, user := checkUser(d.Account, at)
	if !checkCaptcha(c, fmt.Sprintf("login:%s", d.Account), *d.Captcha) {
		return
	}

	// 验证证码登录时首次登录注册
	if !hasUser {
		firstLogin(c, d, at)
		return
	}

	utils.Resp.Success(c, utils.RespOpt.WithData(utils.H{
		"userId":    user.UserId,
		"nickname":  user.Nickname,
		"avatarUrl": utils.Oss.BuildUrl(*user.AvatarUrl),
		"token":     utils.TokenManager.Add(*user.UserId),
	}))
}

// 验证码登录 首次登录注册
func firstLogin(c *gin.Context, d dto.LoginDto, at int) {
	userId := utils.GenerateSnowflakeId()

	if at == 1 {
		repo.UserRepo.Create(model.User{
			UserId:   &userId,
			Nickname: new("萌新用户"),
			Email:    &d.Account,
		})
	} else {
		repo.UserRepo.Create(model.User{
			UserId:   &userId,
			Nickname: new("萌新用户"),
			Phone:    &d.Account,
		})
	}

	utils.Resp.Success(c, utils.RespOpt.WithData(utils.H{
		"userId":    userId,
		"nickname":  new("萌新用户"),
		"avatarUrl": utils.Oss.BuildUrl("default-avatar.webp"),
		"token":     utils.TokenManager.Add(userId),
	}))
}
