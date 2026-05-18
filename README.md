# BookThrift API

FastAPI backend for the BookThrift application.

## Project Structure

```
bookthrift_be/
├── app/
│   ├── routes/          # API route handlers
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic schemas
│   └── __init__.py
├── main.py              # Application entry point
├── config.py            # Configuration settings
├── requirements.txt     # Project dependencies
├── .env.example         # Environment variables example
└── README.md            # This file
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Run the Application

```bash
python main.py
# Or using uvicorn directly:
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

### Adding Routes

Create route files in `app/routes/` and import them in `main.py`:

```python
from app.routes import books
app.include_router(books.router)
```

### Database Models

Define SQLAlchemy models in `app/models/`

### Schemas

Define Pydantic schemas for request/response validation in `app/schemas/`
# book_thrift_be
