package service

import (
	"MomentLingo/common"
	"MomentLingo/dto"
	"MomentLingo/utils"
	"fmt"
	"log/slog"
	"math"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/meilisearch/meilisearch-go"
)

type searchService struct {
}

var SearchService searchService

func (searchService) SearchVocabulary(c *gin.Context, d dto.SearchVocabularyDto) {
	if d.Page <= 0 {
		d.Page = 1
	}

	offset := (d.Page - 1) * d.Limit
	var results = make([]map[string]any, 0)

	// 首页首条优先精准匹配
	if d.Page == 1 {
		res, err := common.MeiliSearch.Index("vocabulary").Search(d.Query, &meilisearch.SearchRequest{
			AttributesToSearchOn:  []string{"word", "translation"},
			AttributesToHighlight: []string{"word", "translation"},
			HighlightPreTag:       "<span class=\"highlight\">",
			HighlightPostTag:      "</span>",
			Filter:                fmt.Sprintf("word = '%s'", escapeValue(d.Query)),
		})

		if err != nil {
			slog.Error("检错异常", "SearchError", err)
			panic("检错异常")
			return
		}

		getSearchResult(&results, res)
	}

	// 分页查询
	res, err := common.MeiliSearch.Index("vocabulary").Search(d.Query, &meilisearch.SearchRequest{
		Limit:                 int64(d.Limit),
		Offset:                int64(offset),
		AttributesToSearchOn:  []string{"word", "translation"},
		AttributesToHighlight: []string{"word", "translation"},
		HighlightPreTag:       "<span class=\"highlight\">",
		HighlightPostTag:      "</span>",
		Sort:                  []string{"weight:desc"},
		Filter:                fmt.Sprintf("word != '%s'", escapeValue(d.Query)),
	})

	if err != nil {
		slog.Error("搜索出错", "SearchError", err)
		panic("搜索出错")
		return
	}

	getSearchResult(&results, res)

	total := int(math.Ceil(float64(res.EstimatedTotalHits)))
	pages := int(math.Ceil(float64(res.EstimatedTotalHits) / float64(d.Limit)))

	entity := utils.BuildPageEntity(d.Page, pages, total, results)
	utils.Resp.Success(c, utils.RespOpt.WithData(entity))
}

func getSearchResult(results *[]map[string]any, resp *meilisearch.SearchResponse) {
	hitsString := utils.JSON.Stringify(resp.Hits)
	hits := utils.JSON.ToArray(hitsString)

	for _, hit := range hits {
		hitMap, ok := hit.(map[string]any)
		if !ok {
			continue
		}

		formatted, exists := hitMap["_formatted"]
		if !exists {
			formatted = map[string]any{}
		}

		delete(hitMap, "_formatted")
		hitMap["highlight"] = formatted

		*results = append(*results, hitMap)
	}
}

// 安全转义
func escapeValue(value string) string {
	escaped := strings.ReplaceAll(value, "\\", "\\\\")
	escaped = strings.ReplaceAll(escaped, "\"", "\\\"")
	return escaped
}
