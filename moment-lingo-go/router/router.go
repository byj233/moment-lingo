package router

import (
	"MomentLingo/controller"
	"MomentLingo/errs"
	"MomentLingo/utils"
	"errors"
	"fmt"
	"log/slog"
	"strings"
	"sync"

	"github.com/gin-contrib/cors"
	"github.com/gin-contrib/gzip"
	"github.com/gin-gonic/gin"
)

type routePattern struct {
	method     string
	pathPrefix string
	matchType  int
}

const (
	matchExact = iota
	matchSingle
	matchWildcard
)

var (
	includePatterns []routePattern
	excludePatterns []routePattern
	patternsOnce    sync.Once
)

func compilePatterns(patterns []string) []routePattern {
	result := make([]routePattern, 0, len(patterns))
	for _, p := range patterns {
		parts := strings.SplitN(p, " ", 2)
		if len(parts) != 2 {
			continue
		}
		rp := routePattern{method: parts[0]}
		path := parts[1]
		switch {
		case strings.HasSuffix(path, "**"):
			rp.matchType = matchWildcard
			rp.pathPrefix = strings.TrimSuffix(path, "**")
		case strings.HasSuffix(path, "*"):
			rp.matchType = matchSingle
			rp.pathPrefix = strings.TrimSuffix(path, "*")
		default:
			rp.matchType = matchExact
			rp.pathPrefix = path
		}
		result = append(result, rp)
	}
	return result
}

func matchRoute(pattern routePattern, method, path string) bool {
	if pattern.method != "*" && pattern.method != method {
		return false
	}
	switch pattern.matchType {
	case matchWildcard:
		return strings.HasPrefix(path, pattern.pathPrefix)
	case matchSingle:
		if !strings.HasPrefix(path, pattern.pathPrefix) {
			return false
		}
		remaining := strings.TrimPrefix(path, pattern.pathPrefix)
		return !strings.Contains(remaining, "/")
	default:
		return pattern.pathPrefix == path
	}
}

func InitRouter() {
	r := gin.Default()
	r.Use(corsMiddleware())
	r.Use(authMiddleWare())
	r.Use(gzip.Gzip(gzip.DefaultCompression))
	r.Use(recoveryMiddleWare())

	// 注册路由
	registerGroup(r)

	err := r.Run(":8080")
	if err != nil {
		panic(fmt.Errorf("gin启动失败 %v", err))
	}
}

func registerGroup(r *gin.Engine) {
	api := r.Group("/moment-lingo")
	r.NoRoute(func(context *gin.Context) {
		utils.Resp.Error(context, "API接口不存在或请求方法错误", utils.RespOpt.WithCode(404))
	})

	authGroup(api)
	vocabularyGroup(api)
	searchGroup(api)
	ttsGroup(api)
	ossGroup(api)
	aiGroup(api)
	essayGroup(api)
	bookGroup(api)
	userGroup(api)
}

func recoveryMiddleWare() gin.HandlerFunc {
	return func(c *gin.Context) {
		defer func() {
			if err := recover(); err != nil {
				switch panicErr := err.(type) {
				case errs.CustomError:
					utils.Resp.Error(c, panicErr.Msg, utils.RespOpt.WithCode(panicErr.Code))
				case *errs.CustomError:
					utils.Resp.Error(c, panicErr.Msg, utils.RespOpt.WithCode(panicErr.Code))
				case error:
					if _, ok := errors.AsType[*errs.CustomError](panicErr); ok {
						slog.Error("服务器内部错误", "Error", err)
						utils.Resp.Error(c, "服务器内部错误")
					} else {
						slog.Error("服务器内部错误", "Error", err)
						utils.Resp.Error(c, "服务器内部错误")
					}
				default:
					slog.Error("服务器内部错误", "Error", err)
					utils.Resp.Error(c, "服务器内部错误")
				}
				c.Abort()
			}
		}()
		c.Next()
	}
}

func authMiddleWare() gin.HandlerFunc {
	patternsOnce.Do(func() {
		includePatterns = compilePatterns([]string{
			"* /ai/**",
			"* /essay/**",
			"* /book/**",
			"* /oss/**",
			"* /user/**",
			"* /auth/options",
		})
		excludePatterns = compilePatterns([]string{
			"* /oss/presign",
		})
	})

	return func(c *gin.Context) {
		currentMethod := c.Request.Method
		currentPath := strings.TrimPrefix(c.FullPath(), "/moment-lingo")

		for _, p := range excludePatterns {
			if matchRoute(p, currentMethod, currentPath) {
				c.Next()
				return
			}
		}

		for _, p := range includePatterns {
			if matchRoute(p, currentMethod, currentPath) {
				authHeader := c.GetHeader("Authorization")
				if authHeader == "" {
					utils.Resp.Error(c, "请求头中缺少Authorization字段", utils.RespOpt.WithCode(401))
					c.Abort()
					return
				}

				parts := strings.SplitN(authHeader, " ", 2)
				if !(len(parts) == 2 && parts[0] == "Bearer") {
					utils.Resp.Error(c, "Authorization格式错误，应为 Bearer <token>", utils.RespOpt.WithCode(401))
					c.Abort()
					return
				}

				token := parts[1]
				userId := utils.TokenManager.Validate(token)
				if userId == nil {
					utils.Resp.Error(c, "登录已过期，请重新登录", utils.RespOpt.WithCode(401))
					c.Abort()
					return
				}

				c.Set("userId", *userId)
				c.Next()
				return
			}
		}

		c.Next()
	}
}

func corsMiddleware() gin.HandlerFunc {
	return cors.New(cors.Config{
		// 允许所有来源，生产环境中应指定具体来源
		AllowOrigins: []string{"*"},
		// 允许的请求方法
		AllowMethods: []string{"GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"},
		// 允许的请求头（显式列出实际需要的，如 Authorization、Content-Type 等）
		AllowHeaders: []string{"Authorization", "Content-Type"},
		// 允许前端获取的响应头
		ExposeHeaders: []string{"Content-Length"},
	})
}

func authGroup(r *gin.RouterGroup) {
	g := r.Group("/auth")
	g.POST("/captcha/send", controller.AuthController.SendCaptcha)
	g.POST("/register", controller.AuthController.Register)
	g.POST("/login", controller.AuthController.Login)
	g.Any("/options", controller.AuthController.Options)
}

func vocabularyGroup(r *gin.RouterGroup) {
	g := r.Group("/vocabulary")
	g.GET("/detail/:vocabularyId", controller.VocabularyController.GetDetailVocabulary)
	g.GET("/brief/:vocabularyId", controller.VocabularyController.GetBriefVocabulary)
	g.GET("/:vocabulary", controller.VocabularyController.GetVocabulary)
}

func searchGroup(r *gin.RouterGroup) {
	g := r.Group("/search")
	g.POST("/vocabulary", controller.SearchController.SearchVocabulary)
}

func ttsGroup(r *gin.RouterGroup) {
	g := r.Group("/tts")
	g.POST("/stream", controller.TtsController.TtsStream)
	g.GET("/voices/list", controller.TtsController.ListVoices)
}

func ossGroup(r *gin.RouterGroup) {
	g := r.Group("/oss")
	g.GET("/sts-token", controller.OssController.GetStsToken)
	g.GET("/presign", controller.OssController.Presign)
	g.POST("/upload/task", controller.OssController.PutUploadTask)
	g.GET("/upload/task/:taskId", controller.OssController.GetUploadTask)
}

func aiGroup(r *gin.RouterGroup) {
	g := r.Group("/ai")
	g.POST("/ocr", controller.AIController.OCR)
	g.POST("/extension/translate", controller.AIController.ExtensionTranslate)
	g.POST("/write", controller.AIController.AIWrite)
}

func essayGroup(r *gin.RouterGroup) {
	g := r.Group("/essay")
	g.POST("/correct/task", controller.EssayController.PutEssayCorrectTask)
	g.GET("/correct/task/list", controller.EssayController.ListEssayCorrectTask)
	g.GET("/correct/list", controller.EssayController.ListEssayCorrect)
	g.GET("/correct/:essayId", controller.EssayController.GetEssayCorrect)
	g.GET("/correct/task/:taskId", controller.EssayController.GetEssayCorrectTask)
}

func bookGroup(r *gin.RouterGroup) {
	g := r.Group("/book")
	g.GET("/list", controller.BookController.ListBooks)
	g.GET("/:bookId", controller.BookController.GetBook)
	g.GET("/detail/:bookId", controller.BookController.ListBookDetail)
}

func userGroup(r *gin.RouterGroup) {
	g := r.Group("/user")
	g.GET("/me", controller.UserController.GetUser)
	g.PATCH("/me", controller.UserController.PatchUser)
}
