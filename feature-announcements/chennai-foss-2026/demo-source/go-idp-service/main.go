package main

import (
	"encoding/json"
	"log"
	"net/http"
)

func main() {
	http.HandleFunc("/healthz", func(w http.ResponseWriter, _ *http.Request) {
		_ = json.NewEncoder(w).Encode(map[string]string{
			"status": "ok",
			"service": "go-idp-service",
		})
	})

	log.Println("go-idp-service listening on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
