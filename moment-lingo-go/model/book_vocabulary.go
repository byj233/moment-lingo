package model

type BookVocabulary struct {
	BookVocabularyId *int `gorm:"primaryKey" json:"bookVocabularyId,string"`
	BookId           *int `json:"bookId,string"`
	VocabularyId     *int `json:"vocabularyId,string"`
	Rank             *int `json:"rank"`
}

func (BookVocabulary) TableName() string {
	return "book_vocabulary"
}
