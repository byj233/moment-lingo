package model

import (
	"MomentLingo/utils"

	"gorm.io/datatypes"
)

type Essay struct {
	EssayId *int64          `gorm:"primaryKey" json:"essayId,string"`
	UserId  *int64          `json:"userId,string"`
	Content *string         `json:"content"`
	Result  *datatypes.JSON `gorm:"type:json" json:"result"`
	// 1 作文批改 2 作文润色
	Type      *int        `json:"type"`
	CreatedAt *utils.Time `gorm:"type:datetime;default:current_timestamp" json:"createdAt"`
	UpdatedAt *utils.Time `gorm:"type:datetime;default:current_timestamp" json:"updatedAt"`
}

func (Essay) TableName() string {
	return "essay"
}
