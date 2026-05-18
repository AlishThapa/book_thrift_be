# Agent Rules and Guidelines

This project follows specific rules for AI agents to ensure consistency and proper documentation.

## Documentation Rules
- **API Updates**: If a new API endpoint is created or an existing one is modified, the `ENDPOINTS.md` file **must** be updated immediately to reflect the changes.
- **Code Standards**: Maintain consistency with the existing FastAPI structure (Models, Schemas, Routes).

## Development Practices
- Use Pydantic schemas for request validation and response modeling.
- Follow the established directory structure:
    - `app/models/`: SQLAlchemy database models.
    - `app/schemas/`: Pydantic data validation schemas.
    - `app/routes/`: API endpoint definitions.
- Ensure all new routes are registered in `main.py` (via routers).

## Response Consistency Rules
- **Success Responses**: All successful API responses must have a `data` key and a `message` key.
    - `data`: Can be any type (list, object, string, int, etc.) containing the actual response data.
    - `message`: Must be a string containing a success message.
    Example:
    ```json
    {
      "data": ...,
      "message": "Operation successful"
    }
    ```
- **Error Responses**: All error responses must have a `details` key containing the error message as a string.
    Example:
    ```json
    {
      "details": "Unauthorized"
    }
    ```