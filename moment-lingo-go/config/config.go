package config

import (
	"fmt"
	"time"

	"github.com/spf13/viper"
)

type Config struct {
	Database    DBConfig     `mapstructure:"database"`
	Redis       RedisConfig  `mapstructure:"redis"`
	Email       EmailConfig  `mapstructure:"email"`
	MeiliSearch MeiliSearch  `mapstructure:"meilisearch"`
	Python      PythonConfig `mapstructure:"python"`
	AliYun      AliYun       `mapstructure:"aliyun"`
}

type DBConfig struct {
	Host     string `mapstructure:"host"`
	Port     int    `mapstructure:"port"`
	Username string `mapstructure:"username"`
	Password string `mapstructure:"password"`
	DB       string `mapstructure:"db"`
}

type RedisConfig struct {
	Host     string `mapstructure:"host"`
	Port     int    `mapstructure:"port"`
	Username string `mapstructure:"username"`
	Password string `mapstructure:"password"`
	DB       int    `mapstructure:"db"`
}

type EmailConfig struct {
	Host     string `mapstructure:"host"`
	Port     int    `mapstructure:"port"`
	Username string `mapstructure:"username"`
	Password string `mapstructure:"password"`
}

type MeiliSearch struct {
	Url    string `mapstructure:"url"`
	ApiKey string `mapstructure:"api-key"`
}

type PythonConfig struct {
	Url string `mapstructure:"url"`
}

type AliYun struct {
	AccessKeyId     string `mapstructure:"access-key-id"`
	AccessKeySecret string `mapstructure:"access-key-secret"`
}

var Conf *Config

func LoadConfig() {
	viper.AddConfigPath("config")
	viper.SetConfigName("application")
	viper.SetConfigType("yml")
	// 时区配置
	loc, err := time.LoadLocation("Asia/Shanghai")
	if err != nil {
		panic(fmt.Errorf("时区配置加载失败 %w", err))
	}
	time.Local = loc

	err = viper.ReadInConfig()
	if err != nil {
		panic(fmt.Errorf("配置文件加载失败 %w", err))
	}

	err = viper.Unmarshal(&Conf)
	if err != nil {
		panic(fmt.Errorf("配置文件加载失败 %w", err))
	}

	return
}
