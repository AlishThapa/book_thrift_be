# BookThrift API Endpoints

This file lists the currently available API endpoints for the BookThrift backend.

## Response Format

- **Success**: `{ "data": ..., "message": "..." }`
- **Error**: `{ "details": "..." }`

## Public Endpoints

- **GET /** — Root
    - Description: Welcome message
    - Authentication: none
    - Response: JSON { "message": "Welcome to BookThrift API" }

- **GET /health** — Health check
    - Description: Returns service health status
    - Authentication: none
    - Response: JSON { "status": "healthy" }

## Authentication & User Endpoints

All routes are prefixed with `/api`.

- **POST /api/register** — Register new user
    - Description: Create a new user account. A permanent `uid` and a persistent `access_token` are generated.
    - Request body (JSON):
        - `full_name` (string)
        - `email` (string, valid email)
        - `password` (string)
        - `phone` (string)
        - `user_type` (string: student, seller, both)
        - `location` (string)
        - `institution` (string)
        - `class_name` (string)
        - `semester` (string)
    - Response: `201 Created` with created user object (including `uid`) in `data`

- **POST /api/login** — Login
    - Description: Authenticate user. Returns the *same* persistent `access_token` every time.
    - Request body (JSON):
        - `email` (string, valid email)
        - `password` (string)
    - Response: `200 OK` with token info and user details (including `uid`, `email`, `full_name`, etc.) in `data`

- **GET /api/get-profile** — Get User Profile
    - Description: Retrieve profile details for the authenticated user
    - Authentication: Bearer Token
    - Response: `200 OK` with user profile object in `data`

- **PUT /api/edit-profile** — Edit User Profile
    - Description: Update profile details for the authenticated user
    - Authentication: Bearer Token
    - Request Body (JSON, all fields optional):
        - `full_name`, `email`, `phone`, `user_type`, `location`, `institution`, `class_name`, `semester`
    - Response: `200 OK` with updated user profile object in `data`

- **DELETE /api/delete-account** — Delete Account
    - Description: Delete the authenticated user's account
    - Authentication: Bearer Token
    - Response: `200 OK`

- **POST /api/forgot-password** — Forgot Password
    - Description: Initiates the password reset process
    - Request Body (JSON):
        - `email`
    - Response: `200 OK`

- **POST /api/reset-password** — Reset Password
    - Description: Resets the user's password
    - Request Body (JSON):
        - `email`, `new_password`
    - Response: `200 OK`

- **POST /api/change-password** — Change Password
    - Description: Allows an authenticated user to change their password
    - Authentication: Bearer Token
    - Request Body (JSON):
        - `old_password`, `new_password`, `confirm_new_password`
    - Response: `200 OK`

## Book Endpoints

All routes are prefixed with `/api`.

- **POST /api/post-book** — Create a book post
    - Description: Post a book for sale with image uploads
    - Authentication: Bearer Token
    - Request Format: `multipart/form-data`
    - Form Fields:
        - `title` (string)
        - `condition` (string: new, like new, used, old)
        - `price` (float)
        - `quantity` (int)
        - `description` (string)
        - `location` (string)
        - `category` (string)
        - `images` (file, multiple allowed, max 5)
    - Response: `201 Created` with created book object in `data`

- **PUT /api/edit-book/{book_id}** — Edit a book post
    - Description: Edit a book's details. Only the owner can edit, and sold books cannot be edited.
    - Authentication: Bearer Token
    - Path Parameter:
        - `book_id` (int, required)
    - Request Body (JSON, all fields optional):
        - `title`, `condition`, `price`, `quantity`, `description`, `location`, `category`, `images`
    - Response: `200 OK` with updated book object in `data`

- **GET /api/delete-book** — Soft-delete a book
    - Description: Soft-deletes a book. Only the owner can delete, and sold books cannot be deleted.
    - Authentication: Bearer Token
    - Query Parameter:
        - `book_id` (int, required)
    - Response: `200 OK`

- **PUT /api/update-book-status/{book_id}** — Mark a book as sold/unsold
    - Description: Allows the owner to change the `is_sold` status of a book.
    - Authentication: Bearer Token
    - Path Parameter:
        - `book_id` (int, required)
    - Query Parameter:
        - `is_sold` (bool, required)
    - Response: `200 OK` with updated book object in `data`

- **GET /api/get-books** — List books (with filters)
    - Description: Get list of books for sale with optional filtering
    - Authentication: Optional (Bearer Token to get `is_wishlisted` status)
    - Query Parameters:
        - `category` (string | list) - filter by one or more categories (e.g., `?category=School&category=Novels`)
        - `search` (string) - search in title or description
        - `min_price` (float) - minimum price filter
        - `max_price` (float) - maximum price filter
    - Response: `200 OK` with list of books in `data`. Each book includes `owner` details and `is_wishlisted` flag.

- **GET /api/book-details** — Get book details
    - Description: Get full details of a single book by ID
    - Authentication: Optional (Bearer Token to get `is_wishlisted` status)
    - Query Parameters:
        - `book_id` (int, required) - ID of the book
    - Response: `200 OK` with book object (including nested `owner` details and `is_wishlisted` flag) in `data`

- **POST /api/toggle-wishlist** — Toggle wishlist status
    - Description: Adds a book to the user's wishlist if it's not already there, or removes it if it is.
    - Authentication: Bearer Token
    - Query Parameters:
        - `book_id` (int, required) - ID of the book
    - Response: `200 OK` with updated wishlist status `{"book_id": ..., "is_wishlisted": ...}` in `data`

- **GET /api/wishlist** — Get user's wishlist
    - Description: Returns a list of books that the authenticated user has wishlisted.
    - Authentication: Bearer Token
    - Response: `200 OK` with list of wishlisted books in `data`. Each book includes `is_wishlisted` as `true`.

- **GET /api/my-listings** — Get user's book listings
    - Description: Returns a list of all books the authenticated user has posted, with an option to filter by status.
    - Authentication: Bearer Token
    - Query Parameters:
        - `listing_status` (string, optional, default: "active") - Filter by status. Can be `active`, `sold`, or `all`.
    - Response: `200 OK` with a list of book objects in `data`.

## Bin Endpoints

All routes are prefixed with `/api`.

- **GET /api/bin** — Get user's bin
    - Description: Returns a list of books that the authenticated user has soft-deleted.
    - Authentication: Bearer Token
    - Response: `200 OK` with a list of book objects in `data`.

- **POST /api/books/{book_id}/recover** — Recover a soft-deleted book
    - Description: Recovers a book from the user's bin.
    - Authentication: Bearer Token
    - Path Parameter:
        - `book_id` (int, required) - ID of the book to recover.
    - Response: `200 OK` with a success message.

- **DELETE /api/bin/{book_id}** — Permanently delete a book
    - Description: Permanently deletes a book from the user's bin.
    - Authentication: Bearer Token
    - Path Parameter:
        - `book_id` (int, required) - ID of the book to permanently delete.
    - Response: `200 OK` with a success message.

## Cart Endpoints

All routes are prefixed with `/api/cart`.

- **POST /api/cart/add** — Add Book to Cart
    - Description: Adds a book to the user's cart or increments its quantity if it already exists. Validates against available stock.
    - Authentication: Bearer Token
    - Request Body (JSON):
        - `book_id` (int, required)
    - Response: `200 OK` with updated cart amount `{"cart_amount": ...}` in `data`
    - Error Responses:
        - `400 Bad Request` if `cart_amount >= book.quantity` (e.g. `{"details": "Cannot add more. Only {quantity} copy/copies available."}`)

- **POST /api/cart/decrement** — Decrement Book Quantity in Cart
    - Description: Decrements the quantity of a book in the user's cart by 1. The quantity will not go below 1.
    - Authentication: Bearer Token
    - Request Body (JSON):
        - `book_id` (int, required)
    - Response: `200 OK` with updated cart amount `{"cart_amount": ...}` in `data`
    - Error Responses:
        - `404 Not Found` if the book is not in the cart.

- **DELETE /api/cart/remove** — Remove Book(s) from Cart
    - Description: Removes one or more books from the user's cart.
    - Authentication: Bearer Token
    - Request Body (JSON):
        - `book_ids` (list of int, required) - A list of book IDs to remove.
    - Response: `200 OK` with the count of deleted items `{"deleted_count": ...}` in `data`
    - Error Responses:
        - `404 Not Found` if no matching books are found in the cart to remove.

- **GET /api/cart** — Get User's Cart data
    - Description: Returns all books in the authenticated user's cart. Includes cart item details (like `cart_amount`) and all nested book details (including available quantity).
    - Authentication: Bearer Token
    - Response: `200 OK` with list of cart items in `data`. Each item includes nested `book` details.

## Static Files

- **GET /uploads/{filename}** — Access uploaded book images