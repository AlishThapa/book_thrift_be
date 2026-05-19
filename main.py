from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
import os
from app.database import create_tables

# Import routers
from app.routes.users import router as users_router
from app.routes.books import router as books_router
from app.routes.cart import router as cart_router
from app.routes.bin import router as bin_router

# Create database tables before starting the app
create_tables()

# Create uploads directory if it doesn't exist
if not os.path.exists("uploads"):
    os.makedirs("uploads")

app = FastAPI(
    title="BookThrift API",
    description="API for BookThrift application",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files to serve uploaded images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Global Exception Handlers for consistent error response
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"details": str(exc.detail)},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_msg = f"{errors[0]['loc'][-1]}: {errors[0]['msg']}" if errors else "Validation Error"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"details": error_msg},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    print(f"Error: {exc}") # Added for debugging
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"details": "An unexpected error occurred."},
    )

# Include routers
app.include_router(users_router)
app.include_router(books_router)
app.include_router(cart_router)
app.include_router(bin_router)

@app.get("/")
async def root():
    return {"message": "Welcome to BookThrift API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)