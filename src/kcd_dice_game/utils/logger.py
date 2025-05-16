"""
Logging utility for the KCD dice game.
"""
import sys
from pathlib import Path
from loguru import logger

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Create logs directory if it doesn't exist
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Configure logger
logger.remove()  # Remove default handler

# Add console handler for DEBUG and above
logger.add(
    sys.stderr,
    level="DEBUG",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# Add file handler for INFO and above
logger.add(
    LOGS_DIR / "kcd_dice_game.log",
    level="INFO",
    rotation="10 MB",  # Rotate when file reaches 10 MB
    retention="1 week",  # Keep logs for 1 week
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)

# Export logger instance
__all__ = ["logger"]
