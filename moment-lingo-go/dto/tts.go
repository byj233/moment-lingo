package dto

type TtsDto struct {
	Content  string `json:"content" binding:"required"`
	Model    string `json:"model" binding:"required,oneof=edge-tts doubao-tts"`
	VoiceKey string `json:"voiceKey" binding:"required"`
}
