"""Centralized configuration for MoneyMentor AI backend."""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GPT_MODEL: str = os.getenv("GPT_MODEL", "gpt-4o-mini")
    GPT_VISION_MODEL: str = "gpt-4o"
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    MAX_PDF_SIZE_MB: int = 10
    MAX_PDF_PAGES: int = 8
    TEMP_DIR: str = os.getenv("TEMP_DIR", "/tmp/moneymentor")


settings = Settings()
