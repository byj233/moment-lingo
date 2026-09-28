package utils

import (
	"database/sql/driver"
	"time"

	"gorm.io/gorm"
	"gorm.io/gorm/schema"
)

type Time time.Time

func (t Time) MarshalJSON() ([]byte, error) {
	if time.Time(t).IsZero() {
		return []byte("null"), nil
	}
	return []byte(`"` + time.Time(t).Format(time.DateTime) + `"`), nil
}

func (t *Time) UnmarshalJSON(data []byte) error {
	if string(data) == "null" {
		return nil
	}
	pt, err := time.Parse(time.DateTime, string(data))
	if err != nil {
		return err
	}
	*t = Time(pt)
	return nil
}

func (t Time) Value() (driver.Value, error) {
	return time.Time(t), nil
}

func (t *Time) Scan(value interface{}) error {
	switch v := value.(type) {
	case time.Time:
		*t = Time(v)
		return nil
	case []byte:
		pt, err := time.Parse(time.DateTime, string(v))
		if err != nil {
			return err
		}
		*t = Time(pt)
		return nil
	case string:
		pt, err := time.Parse(time.DateTime, v)
		if err != nil {
			return err
		}
		*t = Time(pt)
		return nil
	default:
		return nil
	}
}

func (Time) GormDataType() string {
	return "datetime"
}

func (Time) GormDBDataType(db *gorm.DB, field *schema.Field) string {
	switch db.Dialector.Name() {
	case "mysql", "sqlite":
		return "datetime"
	case "postgres":
		return "timestamp"
	default:
		return "datetime"
	}
}
