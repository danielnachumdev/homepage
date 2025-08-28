import os
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# Import the API router directly since we're running this file directly
from src.api import router as api_router
APP_PATH = "__main__:app"

# Create FastAPI app instance
app = FastAPI(
    title="Homepage Backend API",
    description="Backend API for homepage management with Docker container management capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_router)

# Root endpoint


@app.get("/")
async def root():
    """Root endpoint providing basic API information"""
    return {
        "message": "Homepage Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "api": "/api"
    }

# Health check endpoint


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "homepage-backend"}


def main():
    """Main function to run the FastAPI application"""
    load_dotenv()
    # Configuration from environment variables
    host = os.getenv("HOST", "localhost")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info")

    print(f"Starting Homepage Backend API...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Reload: {reload}")
    print(f"Log Level: {log_level}")
    print("-" * 50)
    print(f"API Documentation: http://{host}:{port}/docs")
    print(f"ReDoc Documentation: http://{host}:{port}/redoc")
    print(f"API Base URL: http://{host}:{port}/api")
    print(f"Health Check: http://{host}:{port}/health")
    print("-" * 50)

    # Run the FastAPI application
    uvicorn.run(
        APP_PATH,
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        access_log=True
    )


if __name__ == "__main__":
    main()
