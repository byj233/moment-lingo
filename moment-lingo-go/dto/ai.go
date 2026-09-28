package dto

type OCRDto struct {
	ImageUrl string `json:"imageUrl" binding:"required"`
}

type ExtensionTranslateDto struct {
	Content string `json:"content" binding:"required"`
}

type AIWriteDto struct {
	Content     string `json:"content" binding:"required"`
	Corrections []any  `json:"corrections" binding:"required"`
}
