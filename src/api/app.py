from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from src.api.routes import router
from src.utils.logger import setup_logging, get_logger
from src.utils.database import db_manager
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from src.utils.config import config_manager

# Setup logging
setup_logging()
logger = get_logger("app")

# Initialize Sentry if DSN is provided
if (config_manager.settings.sentry_dsn and 
    config_manager.settings.sentry_dsn.strip() and 
    config_manager.settings.sentry_dsn != "your_sentry_dsn"):
    sentry_sdk.init(
        dsn=config_manager.settings.sentry_dsn,
        integrations=[FastApiIntegration()],
        traces_sample_rate=1.0,
        environment=config_manager.settings.environment
    )

# Create FastAPI app
app = FastAPI(
    title="Hapivet Prompt Library",
    description="A comprehensive prompt library with AI model routing, cost optimization, and usage monitoring",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        # Create database tables
        db_manager.create_tables()
        logger.info("Database tables created successfully")
        
        # Initialize other services
        logger.info("Hapivet Prompt Library started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Hapivet Prompt Library")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Hapivet Prompt Library",
        "version": "1.0.0",
        "docs": "/docs",
        "examples": "/examples",
        "health": "/api/v1/health"
    }


@app.get("/examples", response_class=HTMLResponse)
async def examples_page():
    """Interactive examples page"""
    return FileResponse("static/examples.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 