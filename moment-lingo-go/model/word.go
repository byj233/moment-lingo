package model

import "gorm.io/datatypes"

type Word struct {
	WordId       *int            `gorm:"primaryKey" json:"wordId,string"`
	VocabularyId *int            `json:"vocabularyId,string"`
	Word         *string         `json:"word"`
	Brief        *datatypes.JSON `gorm:"type:json" json:"brief"`
	Content      *datatypes.JSON `gorm:"type:json" json:"content"`
	Tags         *datatypes.JSON `gorm:"type:json" json:"tags"`
	Translation  *datatypes.JSON `gorm:"type:json" json:"translation"`
}

func (Word) TableName() string {
	return "word"
}
