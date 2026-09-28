package model

import (
	"MomentLingo/utils"

	"gorm.io/datatypes"
)

type Voice struct {
	VoiceId   *int            `gorm:"primaryKey" json:"voiceId,string"`
	VoiceName *string         `json:"voiceName"`
	VoiceKey  *string         `json:"voiceKey"`
	Type      *string         `json:"type"`
	Model     *string         `json:"model"`
	Tags      *datatypes.JSON `gorm:"type:json" json:"tags"`
	Weight    *int            `json:"weight"`
	CreatedAt *utils.Time     `gorm:"type:datetime;autoCreateTime" json:"createdAt"`
	UpdatedAt *utils.Time     `gorm:"type:datetime;autoUpdateTime" json:"updatedAt"`
}

func (Voice) TableName() string {
	return "voice"
}
