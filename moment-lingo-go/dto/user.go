package dto

type PatchUserDto struct {
	Nickname  *string `json:"nickname"`
	AvatarUrl *string `json:"avatarUrl"`
}
