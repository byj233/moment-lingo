package model

import "gorm.io/datatypes"

type Vocabulary struct {
	VocabularyId *int            `gorm:"primaryKey" json:"vocabularyId,string"`
	Vocabulary   *string         `json:"vocabulary"`
	Phonetic     *string         `json:"phonetic"`
	Translation  *datatypes.JSON `gorm:"type:json" json:"translation"`
	Explanation  *datatypes.JSON `gorm:"type:json" json:"explanation"`
	Tags         *datatypes.JSON `gorm:"type:json" json:"tags"`
	Did          *string         `json:"did"`
	Done         *string         `json:"done"`
	Doing        *string         `json:"doing"`
	Does         *string         `json:"does"`
	Comparative  *string         `json:"comparative"`
	Superlative  *string         `json:"superlative"`
	Plural       *string         `json:"plural"`
	Lemma        *string         `json:"lemma"`
	LexicalId    *int            `json:"lexicalId"`
	Type         *string         `json:"type"`
}

func (Vocabulary) TableName() string {
	return "vocabulary"
}
