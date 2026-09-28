package model

import (
	"MomentLingo/utils"

	"gorm.io/datatypes"
)

type Book struct {
	BookId       *int            `gorm:"primaryKey" json:"bookId,string"`
	BookOriginId *string         `json:"bookOriginId"`
	WordCount    *int            `json:"wordCount"`
	Title        *string         `json:"title"`
	Tags         *datatypes.JSON `gorm:"type:json" json:"tags"`
	CreatedAt    *utils.Time     `gorm:"type:datetime;default:current_timestamp" json:"createdAt"`
	UpdatedAt    *utils.Time     `gorm:"type:datetime;default:current_timestamp" json:"updatedAt"`
}

func (Book) TableName() string {
	return "book"
}
