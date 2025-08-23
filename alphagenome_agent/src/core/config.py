"""Configuration management for TestBase Research."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""
    
    ALPHAGENOME_API_KEY: Optional[str] = os.getenv("ALPHAGENOME_API_KEY")
    ALPHAGENOME_BASE_URL: str = os.getenv(
        "ALPHAGENOME_BASE_URL", 
        "https://alphagenome.googleapis.com/v1"
    )
    
    USE_MOCK: bool = os.getenv("USE_MOCK", "0") == "1"
    
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    OUTPUT_DIR: Path = DATA_DIR / "outputs"
    FIGURES_DIR: Path = OUTPUT_DIR / "figures"
    FIXTURES_DIR: Path = PROJECT_ROOT / "src" / "tests" / "fixtures"
    
    DEFAULT_WINDOW_SIZE: int = 25000
    MAX_INTERVAL_SIZE: int = 1_000_000
    
    RETRY_MAX_ATTEMPTS: int = 3
    RETRY_WAIT_SECONDS: float = 1.0
    RETRY_MAX_WAIT: float = 10.0
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist."""
        for dir_path in [cls.DATA_DIR, cls.OUTPUT_DIR, cls.FIGURES_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)


config = Config()