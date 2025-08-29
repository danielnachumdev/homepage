from contextlib import asynccontextmanager
import os
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from src.db import get_db, DatabaseInitializer
from src.api import router as api_router
from src.utils.logger import get_logger

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = get_logger("lifespan")

    # ================== SETUP ==================
    logger.info("Starting application setup...")
    db = get_db()
    await DatabaseInitializer().init_db(db)
    logger.info("Application setup completed successfully")
    # ================== END SETUP ==================
    yield
    # ================== SHUTDOWN ==================
    logger.info("Starting application shutdown...")
    await db.disconnect()  # type: ignore
    logger.info("Application shutdown completed")
    # ================== END SHUTDOWN ==================


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

    # Get logger instance
    logger = get_logger("main")

    # Configuration from environment variables
    host = os.getenv("HOST", "localhost")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info")

    logger.info("Starting Homepage Backend API...")
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"Reload: {reload}")
    logger.info(f"Log Level: {log_level}")
    logger.info("-" * 50)
    logger.info(f"API Documentation: http://{host}:{port}/docs")
    logger.info(f"ReDoc Documentation: http://{host}:{port}/redoc")
    logger.info(f"API Base URL: http://{host}:{port}/api")
    logger.info(f"Health Check: http://{host}:{port}/health")
    logger.info("-" * 50)

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
