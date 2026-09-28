package dto

type EssayCorrectDto struct {
	Content string `json:"content" binding:"required"`
}
