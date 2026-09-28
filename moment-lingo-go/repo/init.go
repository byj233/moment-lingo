package repo

import (
	"MomentLingo/model"

	"gorm.io/gorm"
)

func InitRepo(db *gorm.DB) {
	UserRepo.G = gorm.G[model.User](db)
	VocabularyRepo.G = gorm.G[model.Vocabulary](db)
	WordRepo.G = gorm.G[model.Word](db)
	PhraseRepo.G = gorm.G[model.Phrase](db)
	VoiceRepo.G = gorm.G[model.Voice](db)
	EssayRepo.G = gorm.G[model.Essay](db)
	BookRepo.G = gorm.G[model.Book](db)
	BookVocabularyRepo.G = gorm.G[model.BookVocabulary](db)
}
