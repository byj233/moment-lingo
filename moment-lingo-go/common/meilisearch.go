package common

import (
	"MomentLingo/config"

	"github.com/meilisearch/meilisearch-go"
)

var MeiliSearch meilisearch.ServiceReader

func InitMeiliSearch(cfg config.MeiliSearch) {
	MeiliSearch = meilisearch.New(cfg.Url, meilisearch.WithAPIKey(cfg.ApiKey))
}
