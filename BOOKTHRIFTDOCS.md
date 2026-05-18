# BookThrift API Documentation

This document provides information about the BookThrift API, its endpoints, and implementation details.

## Why JWT (JSON Web Token)?

We have implemented JWT-based authentication for the following reasons:

1.  **Security**: Instead of passing sensitive user identifiers like `user_id` in every request, we use a signed token. This token ensures that the user is who they claim to be and that the data hasn't been tampered with.
2.  **Scalability**: JWT is stateless. The server doesn't need to store session information in the database for every user. All the information required to identify the user is contained within the token itself.
3.  **Efficiency**: Once a user is authenticated, they receive a token. This token is then sent in the `Authorization` header (`Bearer <token>`) for subsequent requests, making the communication streamlined and secure.
4.  **Standardized**: JWT is a widely used industry standard, making it easier to integrate with various front-end applications (like our Android app) and third-party services.

## Implementation Details

-   **Secret Key**: Used to sign the tokens (stored in environment variables).
-   **Algorithm**: HS256 is used for signing.
-   **Expiration**: Tokens have a limited lifespan for enhanced security.
-   **Authorization Header**: Clients must include the token in the header as: `Authorization: Bearer <your_jwt_token>`.

---

## API Endpoints

### Public Endpoints

-   **GET /** — Root
    -   Description: Welcome message
    -   Authentication: none
    -   Response: JSON `{ "message": "Welcome to BookThrift API" }`

-   **GET /health** — Health check
    -   Description: Returns service health status
    -   Authentication: none
    -   Response: JSON `{ "status": "healthy" }`

### Authentication & User Endpoints
All routes are prefixed with `/api`.

-   **POST /api/register** — Register new user
    -   Description: Create a new user account
    -   Authentication: none
    -   Request body (JSON):
        -   `full_name`, `email`, `password`, `phone`, `user_type`, `location`, `institution`, `class_name`, `semester`
    -   Response: `201 Created` with created user object

-   **POST /api/login** — Login
    -   Description: Authenticate user and receive a JWT token
    -   Authentication: none
    -   Request body (JSON):
        -   `email`, `password`
    -   Response: `200 OK` with `access_token` and `token_type`

-   **GET /api/get-profile** — Get User Profile
    -   Description: Retrieve profile details for the authenticated user
    -   Authentication: **JWT Token Required**
    -   Response: `200 OK` with user profile object

-   **PUT /api/edit-profile** — Edit User Profile
    -   Description: Update profile details for the authenticated user
    -   Authentication: **JWT Token Required**
    -   Request Body (JSON, all fields optional):
        -   `full_name`, `email`, `phone`, `user_type`, `location`, `institution`, `class_name`, `semester`
    -   Response: `200 OK` with updated user profile object

-   **DELETE /api/delete-account** — Delete User Account
    -   Description: Permanently delete the authenticated user's account
    -   Authentication: **JWT Token Required**
    -   Response: `200 OK` with success message

-   **POST /api/forgot-password** — Forgot Password
    -   Description: Initiates the password reset process
    -   Authentication: none
    -   Request Body (JSON): `email`
    -   Response: `200 OK` with a success message

-   **POST /api/reset-password** — Reset Password
    -   Description: Resets the user's password
    -   Authentication: none
    -   Request Body (JSON): `email`, `new_password`
    -   Response: `200 OK` with a success message

-   **POST /api/change-password** — Change Password
    -   Description: Allows an authenticated user to change their password
    -   Authentication: **JWT Token Required**
    -   Request Body (JSON):
        -   `old_password`, `new_password`, `confirm_new_password`
    -   Response: `200 OK` with a success message

## Auto-generated Documentation (FastAPI)
-   **GET /docs** — Swagger UI (interactive API docs)
-   **GET /redoc** — ReDoc UI
-   **GET /openapi.json** — OpenAPI schema
