import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.middleware import (
    RequestLoggingMiddleware, 
    ErrorHandlingMiddleware, 
    SecurityHeadersMiddleware
)
from app.api.routes.v1 import v1_routers
from app.infrastructure.database import engine
from app.services.rbac_service import RBACService

# Import all models to ensure they're registered with the Base
from app.domain.rbac_models import Base, User
from app.domain.customer import Customer
from app.domain.loan_request import LoanRequest
from app.domain.reference_models import Branch, LoanType, RequestType
from app.domain.property_models import Property, LandDetail, BuildingDetail, GoogleMap, Document
from app.domain.location_models import Province, District, Commune, Village, Agency

# Legacy presentation routers are now consolidated into v1 API routes
# All functionality has been moved to app/api/routes/v1/

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("🚀 Starting FastAPI Property Evaluation System...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created/verified")
    
    # Initialize RBAC system
    try:
        from app.infrastructure.database import SessionLocal
        db = SessionLocal()
        try:
            rbac_service = RBACService(db)
            rbac_service.initialize_default_data()
            logger.info("✅ RBAC system initialized with default roles and permissions")
        except Exception as e:
            logger.warning(f"⚠️  RBAC initialization warning: {e}")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"❌ Failed to initialize RBAC system: {e}")
    
    logger.info("🎯 Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down FastAPI Property Evaluation System...")

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="A professional property evaluation system with RBAC authentication",
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan
)

# Add custom middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=settings.allowed_credentials,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers,
)

# All routes are now consolidated under /api/v1
# Legacy routes have been removed to prevent duplicates

# Include API v1 routers under /api/v1
for router in v1_routers:
    app.include_router(router, prefix=settings.api_v1_prefix)

# Root endpoint
@app.get("/")
async def read_root():
    """Root endpoint with application information."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }

# Global exception handler for unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_type": "InternalServerError"
        }
    ) 