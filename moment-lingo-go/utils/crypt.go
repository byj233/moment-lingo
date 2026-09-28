package utils

import (
	"fmt"
	"log/slog"
	"regexp"
	"strings"

	"golang.org/x/crypto/bcrypt"
)

func Encrypt(password string) string {
	p, err := bcrypt.GenerateFromPassword([]byte(password), 14)
	if err != nil {
		slog.Error("加密异常", "EncryptError", err)
		panic(fmt.Errorf("加密异常 %w", err))
	}
	return string(p)
}

func CompareCrypt(hashP, password string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(hashP), []byte(password))
	if err != nil {
		return false
	}

	return true
}

func ValidatePasscode(passcode string) bool {
	passcode = strings.TrimSpace(passcode)
	if len(passcode) < 8 {
		return false
	}

	// 检查是否包含英文（大小写）
	hasLetter, _ := regexp.MatchString(`[a-zA-Z]`, passcode)
	// 检查是否包含数字
	hasNumber, _ := regexp.MatchString(`\d`, passcode)

	if !hasLetter || !hasNumber {
		return false
	}

	return true
}
