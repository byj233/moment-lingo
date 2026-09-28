package dto

type SearchVocabularyDto struct {
	Query string `json:"query" binding:"required"`
	Limit int    `json:"limit" binding:"required"`
	Page  int    `json:"page" binding:"required"`
}
