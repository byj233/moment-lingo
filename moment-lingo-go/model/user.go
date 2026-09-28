package model

import (
	"MomentLingo/utils"
)

type User struct {
	UserId    *int64      `gorm:"primaryKey" json:"userId,string"`
	Nickname  *string     `gorm:"not null" json:"nickname"`
	AvatarUrl *string     `gorm:"not null;default:avatar/default-avatar.webp" json:"avatarUrl"`
	Passcode  *string     `gorm:"not null" json:"passcode"`
	Email     *string     `json:"email"`
	Phone     *string     `json:"phone"`
	CreatedAt *utils.Time `gorm:"type:datetime;default:current_timestamp" json:"createdAt"`
	UpdatedAt *utils.Time `gorm:"type:datetime;default:current_timestamp" json:"updatedAt"`
}

func (User) TableName() string {
	return "user"
}
