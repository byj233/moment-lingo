package dto

type CaptchaDto struct {
	Account string `json:"account" binding:"required"`
	Scene   string `json:"scene" binding:"required,oneof=login register modify"`
}

type RegisterDto struct {
	Nickname string `json:"nickname" binding:"required"`
	Passcode string `json:"passcode" binding:"required"`
	Captcha  string `json:"captcha" binding:"required"`
	Account  string `json:"account" binding:"required"`
}

type LoginDto struct {
	Account  string  `json:"account" binding:"required"`
	Scene    string  `json:"scene" binding:"required,oneof=pwd sms"`
	Passcode *string `json:"passcode"`
	Captcha  *string `json:"captcha"`
}
