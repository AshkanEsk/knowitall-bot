"""Configuration settings for the bot."""

import os
from dataclasses import dataclass
from enum import Enum


class BotMode(Enum):
    """Available bot modes."""
    DICTIONARY = "dictionary"
    GRAMMAR = "grammar"


@dataclass(frozen=True)
class BotConfig:
    """Bot configuration."""
    TELEGRAM_TOKEN: str
    HUGGINGFACE_API_KEY: str
    HF_OWNER: str
    HF_LLM: str
    DEFAULT_MODE: BotMode = BotMode.DICTIONARY
    
    @classmethod
    def from_env(cls) -> "BotConfig":
        """Load configuration from environment variables."""
        # Try RAILWAY_ prefixed variables first (Railway.app style), then standard names
        return cls(
            TELEGRAM_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("RAILWAY_TELEGRAM_BOT_TOKEN"),
            HUGGINGFACE_API_KEY=os.getenv("HUGGINGFACE_API_KEY") or os.getenv("RAILWAY_HUGGINGFACE_API_KEY"),
            HF_OWNER=os.getenv("HF_OWNER") or os.getenv("RAILWAY_HF_OWNER"),
            HF_LLM=os.getenv("HF_LLM") or os.getenv("RAILWAY_HF_LLM"),
            DEFAULT_MODE=BotMode.DICTIONARY  # Always use default, ignore env for this
        )
    
    def validate(self) -> None:
        """Ensure all required settings are present."""
        missing = [
            name for name, value in self.__dict__.items() 
            if value is None and name != "DEFAULT_MODE"
        ]
        if missing:
            # Print debug info
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Environment variables found: {list(os.environ.keys())}")
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")