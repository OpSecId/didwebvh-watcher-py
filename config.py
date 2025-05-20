"""App configuration."""

import logging
import os
from typing import Union

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    PROJECT_TITLE: str = "DID WebVH Watcher"
    PROJECT_VERSION: str = "v0"

    SECRET_KEY: str = os.environ.get("SECRET_KEY", "s3cret")

    POSTGRES_URI: Union[str, None] = os.getenv("POSTGRES_URI")
    POSTGRES_USER: Union[str, None] = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: Union[str, None] = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_SERVER_NAME: Union[str, None] = os.getenv("POSTGRES_SERVER_NAME")
    POSTGRES_SERVER_PORT: Union[str, None] = os.getenv("POSTGRES_SERVER_PORT")

    ASKAR_DB: str = "sqlite://app.db"
    if (
        POSTGRES_USER
        and POSTGRES_PASSWORD
        and POSTGRES_SERVER_NAME
        and POSTGRES_SERVER_PORT
    ) or POSTGRES_URI:
        if not POSTGRES_URI:
            POSTGRES_URI = f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER_NAME}:{POSTGRES_SERVER_PORT}/didwebvh-server"
            
        logging.info(
            f"Using postgres storage: {POSTGRES_URI.split('@')[-1]}"
        )
        
        ASKAR_DB: str = POSTGRES_URI
        
    else:
        logging.info("Using SQLite database")


settings = Settings()
