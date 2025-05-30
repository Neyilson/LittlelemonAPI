# Little Lemon API

A RESTful API for restaurant management. This project allows you to manage users, authentication, menu items, categories, orders, cart, and user roles (managers and delivery crew). Ideal for digitizing and automating restaurant operations.

## Table of Contents

- [Description](#description)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)

## Description

Little Lemon API is designed to streamline restaurant operations by providing endpoints for user registration and authentication, menu and category management, order processing, cart management, and user group assignments. The API is built with Django and Django REST Framework.

## Features

- User registration and authentication
- Menu item and category CRUD operations
- Cart management for customers
- Order creation and management
- User group management (Managers, Delivery Crew)
- Token-based authentication
- Throttling and permissions

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/little-lemon-api.git
   cd little-lemon-api
   ```

2. **Create and activate a virtual environment:**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Apply migrations:**
   ```sh
   python manage.py migrate
   ```

5. **Create a superuser (optional, for admin access):**
   ```sh
   python manage.py createsuperuser
   ```

6. **Run the development server:**
   ```sh
   python manage.py runserver
   ```

## Usage

- Access the API at: `http://127.0.0.1:8000/api/`
- Use tools like [Swagger UI](https://editor.swagger.io/) or [Postman](https://www.postman.com/) to interact with the API.
- API endpoints require authentication for most operations. Obtain a token via the authentication endpoints and include it in your requests.

## API Documentation

The API is documented using OpenAPI (Swagger).  
You can find the documentation in the `openapi.yaml` file or view it using Swagger UI.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for improvements or bug fixes.
