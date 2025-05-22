package utils

import (
	"errors"
	"regexp"
)

// IsValidEmail checks if the provided email address is valid.
func IsValidEmail(email string) (bool, error) {
	if email == "" {
		return false, errors.New("email cannot be empty")
	}
	// Simple regex for validating an email address
	const emailRegex = `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
	re := regexp.MustCompile(emailRegex)
	return re.MatchString(email), nil
}

// FormatString trims whitespace from the beginning and end of a string.
func FormatString(s string) string {
	return strings.TrimSpace(s)
}

// GenerateID creates a simple unique identifier.
func GenerateID() string {
	return uuid.New().String()
}