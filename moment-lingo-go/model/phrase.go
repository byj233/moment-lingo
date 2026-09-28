package model

import "gorm.io/datatypes"

type Phrase struct {
	PhraseId     *int            `gorm:"primaryKey" json:"phraseId,string"`
	VocabularyId *int            `json:"vocabularyId,string"`
	WordId       *int            `json:"wordId,string"`
	Phrase       *string         `json:"phrase"`
	Lemma        *string         `json:"lemma"`
	Tags         *datatypes.JSON `gorm:"type:json" json:"tags"`
	Translation  *datatypes.JSON `gorm:"type:json" json:"translation"`
}

func (Phrase) TableName() string {
	return "phrase"
}
