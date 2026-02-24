"""Entry point for the Dictionary Bot."""

import logging

from telegram.ext import Application, CommandHandler, MessageHandler, filters

from config.settings import BotConfig
from core.definer import Definer
from core.session import SessionManager
from bot.handlers import BotHandlers
from bot.utils import setup_logging, SingleInstanceLock

logger = logging.getLogger(__name__)


def main() -> None:
    """Run the bot."""
    setup_logging()
    
    with SingleInstanceLock():
        # Load configuration
        config = BotConfig.from_env()
        config.validate()
        
        # Initialize components
        definer = Definer(
            hfapi=config.HUGGINGFACE_API_KEY,
            owner=config.HF_OWNER,
            llm=config.HF_LLM
        )
        
        session_manager = SessionManager()
        handlers = BotHandlers(definer, session_manager)
        
        # Build application
        application = Application.builder().token(config.TELEGRAM_TOKEN).build()
        
        # Register command handlers
        application.add_handler(CommandHandler("start", handlers.start))
        application.add_handler(CommandHandler("help", handlers.help))
        application.add_handler(CommandHandler("mode", handlers.mode))
        
        # Register message handler (catches all text)
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_message)
        )
        
        # Register error handler
        application.add_error_handler(handlers.error_handler)
        
        # Run
        logger.info("🤖 Bot is running... Press Ctrl+C to stop.")
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=["message"]
        )


if __name__ == "__main__":
    main()