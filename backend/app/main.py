"""
Hotel PMS - Main Application
FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.api import bookings, webhooks, rooms, reports, health, crud, passport, housekeeping


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print(f"🚀 Starting Hotel PMS API [{settings.env}]")
    
    # Create tables (for SQLite development)
    if settings.database_url.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)
        print("📦 Database tables created (SQLite)")
    
    yield
    
    # Shutdown
    print("👋 Shutting down Hotel PMS API")


# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="""
    ## Hotel Property Management System API
    
    Tích hợp Channel Manager (Channex), Smart Lock (TTLock), và báo cáo XNC.
    
    ### Features
    - 📦 Booking Sync từ Airbnb/Booking/Agoda/Trip
    - 🔐 Auto Passcode Generation
    - 📋 XNC Immigration Report Export
    - 📱 Telegram Notifications
    - 🛂 Passport OCR
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health.router, tags=["Health"])
app.include_router(crud.router, prefix=settings.api_prefix, tags=["CRUD"])
app.include_router(passport.router, prefix=settings.api_prefix, tags=["Passport OCR"])
app.include_router(webhooks.router, prefix=settings.api_prefix, tags=["Webhooks"])
app.include_router(bookings.router, prefix=settings.api_prefix, tags=["Bookings"])
app.include_router(rooms.router, prefix=settings.api_prefix, tags=["Rooms"])
app.include_router(reports.router, prefix=settings.api_prefix, tags=["Reports"])
app.include_router(housekeeping.router, prefix=settings.api_prefix, tags=["Housekeeping"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "environment": settings.env,
        "docs": "/docs"
    }
