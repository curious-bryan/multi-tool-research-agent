# utils/config.py
"""Configuration management for the multi-tool research agent.

This module handles all environment variables, API keys, and agent settings.
Designed to be imported once and used throughout the application.

Setup:
    1. Create a .env file in the project root:
        OPENAI_API_KEY=your_key_here
        ANTHROPIC_API_KEY=your_optional_key_here
    
    2. Import and validate before using:
        from utils.config import Config
        Config.validate()

Example:
    from utils.config import Config
    
    # Use in your agent
    agent = MyAgent(
        model=Config.DEFAULT_MODEL,
        max_tokens=Config.MAX_TOKENS
    )

"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for managing environment variables and settings."""
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    ANTHROPIC_API_KEY: Optional[str] = os.getenv('ANTHROPIC_API_KEY')
    
    # Model Settings
    DEFAULT_MODEL: str = 'gpt-3.5-turbo'
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.7
    
    # Agent Settings
    MAX_ITERATIONS: int = 5
    MEMORY_SIZE: int = 1000
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        return True

