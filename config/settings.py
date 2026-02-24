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
    DEFAULT_MODE: BotMode = BotMode.DICTIONARY  # Hardcoded default
    
    @classmethod
    def from_env(cls) -> "BotConfig":
        """Load configuration from environment variables."""
        return cls(
            TELEGRAM_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN"),
            HUGGINGFACE_API_KEY=os.getenv("HUGGINGFACE_API_KEY"),
            HF_OWNER=os.getenv("HF_OWNER"),
            HF_LLM=os.getenv("HF_LLM"),
            # Remove DEFAULT_MODE from here, use hardcoded default above
        )
    
    def validate(self) -> None:
        """Ensure all required settings are present."""
        missing = [
            name for name, value in self.__dict__.items() 
            if value is None and name != "DEFAULT_MODE"
        ]
        if missing:
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")