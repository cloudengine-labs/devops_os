package main

import (
    "log"
    "net/http"
    "go-project/internal/handlers"
)

func main() {
    // Initialize the HTTP server
    http.HandleFunc("/", handlers.HomeHandler) // Example route
    http.HandleFunc("/api/data", handlers.DataHandler) // Example API route

    // Start the server
    log.Println("Starting server on :8080")
    if err := http.ListenAndServe(":8080", nil); err != nil {
        log.Fatalf("Could not start server: %s\n", err)
    }
}