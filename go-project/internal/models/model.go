package models

// User represents a user in the application.
type User struct {
    ID    int    `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email"`
}

// NewUser creates a new User instance.
func NewUser(id int, name string, email string) *User {
    return &User{
        ID:    id,
        Name:  name,
        Email: email,
    }
}

// UpdateEmail updates the email of the User.
func (u *User) UpdateEmail(newEmail string) {
    u.Email = newEmail
}

// Product represents a product in the application.
type Product struct {
    ID    int     `json:"id"`
    Name  string  `json:"name"`
    Price float64 `json:"price"`
}

// NewProduct creates a new Product instance.
func NewProduct(id int, name string, price float64) *Product {
    return &Product{
        ID:    id,
        Name:  name,
        Price: price,
    }
}

// UpdatePrice updates the price of the Product.
func (p *Product) UpdatePrice(newPrice float64) {
    p.Price = newPrice
}