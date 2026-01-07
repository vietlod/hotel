"""
Hotel PMS - Configuration Module
Loads environment variables and provides typed configuration.
"""
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Environment
    env: str = "development"
    debug: bool = True
    
    # API
    api_title: str = "Hotel PMS API"
    api_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    
    # Database
    database_url: str = "sqlite:///./hotel_pms.db"
    database_echo: bool = False
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Security
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    
    # Channex
    channex_env: str = "staging"
    channex_api_key: str = ""
    channex_base_url: str = "https://staging.channex.io/api/v1"
    channex_webhook_secret: str = ""
    
    # TTLock
    ttlock_region: str = "eu"
    ttlock_client_id: str = ""
    ttlock_client_secret: str = ""
    ttlock_username: str = ""
    ttlock_password_md5: str = ""
    ttlock_api_endpoint: str = "https://euapi.ttlock.com/v3"
    
    # Telegram
    telegram_bot_token: str = ""
    telegram_chat_id_admin: str = ""
    telegram_chat_id_housekeeping: str = ""
    telegram_chat_id_maintenance: str = ""
    
    # XNC Portal
    xnc_portal_url: str = "https://hochiminh.xuatnhapcanh.gov.vn"
    xnc_form_username: str = ""
    xnc_form_password: str = ""
    xnc_auto_upload: bool = False
    
    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export settings instance
settings = get_settings()
