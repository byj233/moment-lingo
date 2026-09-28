package main

import (
	"MomentLingo/common"
	"MomentLingo/config"
	"MomentLingo/repo"
	"MomentLingo/router"
	"log/slog"
	"os"
)

func main() {
	jsonHandler := slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
		Level:     slog.LevelInfo,
		AddSource: true,
	})
	slog.SetDefault(slog.New(jsonHandler))

	config.LoadConfig()
	common.InitDB(config.Conf.Database)
	common.InitRedis(config.Conf.Redis)
	common.InitMeiliSearch(config.Conf.MeiliSearch)

	//gin.SetMode(gin.ReleaseMode)
	repo.InitRepo(common.DB)
	router.InitRouter()
}
