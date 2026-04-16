// Package go_idp_service provides unit tests for go-idp-service.
package go_idp_service_test

import (
	"testing"
)

// TestAdd verifies basic arithmetic — replace with real application tests.
func TestAdd(t *testing.T) {
	result := 1 + 1
	if result != 2 {
		t.Errorf("expected 2, got %d", result)
	}
}

func TestStringContains(t *testing.T) {
	greeting := "Hello from go-idp-service"
	if len(greeting) == 0 {
		t.Error("expected non-empty greeting")
	}
}

func TestTableDriven(t *testing.T) {
	cases := []struct {
		a, b, want int
	}{
		{1, 2, 3},
		{0, 0, 0},
		{-1, 1, 0},
	}
	for _, tc := range cases {
		got := tc.a + tc.b
		if got != tc.want {
			t.Errorf("add(%d, %d) = %d; want %d", tc.a, tc.b, got, tc.want)
		}
	}
}
