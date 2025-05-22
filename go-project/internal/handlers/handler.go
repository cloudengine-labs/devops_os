package handlers

import (
    "encoding/json"
    "net/http"
)

// Example data structure
type Example struct {
    ID   int    `json:"id"`
    Name string `json:"name"`
}

// GetExampleHandler handles GET requests for example data
func GetExampleHandler(w http.ResponseWriter, r *http.Request) {
    example := Example{ID: 1, Name: "Example Name"}
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(example)
}

// PostExampleHandler handles POST requests to create example data
func PostExampleHandler(w http.ResponseWriter, r *http.Request) {
    var example Example
    if err := json.NewDecoder(r.Body).Decode(&example); err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }
    // Here you would typically save the example to a database
    w.WriteHeader(http.StatusCreated)
    json.NewEncoder(w).Encode(example)
}