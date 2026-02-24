"""Telegram bot handlers."""

import html
import logging

from telegram import Update
from telegram.ext import ContextTypes

from config.settings import BotMode
from core.definer import Definer
from core.session import SessionManager

logger = logging.getLogger(__name__)


class BotHandlers:
    """Handles Telegram bot commands and messages."""
    
    WELCOME_TEXT = (
        "👋 Welcome to the Dictionary Bot!\n\n"
        "📚 I can help you with:\n"
        "• Dictionary definitions (/mode dictionary)\n"
        "• Grammar explanations (/mode grammar)\n\n"
        "Current mode: <b>{mode}</b>\n\n"
        "Send me any word to get started!"
    )
    
    HELP_TEXT = (
        "🤖 Available Commands:\n\n"
        "/start - Start the bot\n"
        "/help - Show this help\n"
        "/mode - Show current mode\n"
        "/mode &lt;type&gt; - Switch mode (dictionary/grammar)\n\n"
        "<b>Modes:</b>\n"
        "• <b>Dictionary</b>: Send any word for definition\n"
        "• <b>Grammar</b>: Send any grammar topic for explanation\n\n"
        "Current mode: <b>{mode}</b>"
    )
    
    MODE_SWITCHED_TEXT = (
        "✅ Mode switched to: <b>{mode}</b>\n\n"
        "{instruction}"
    )
    
    MODE_INSTRUCTIONS = {
        BotMode.DICTIONARY: "Send me any word and I'll define it!",
        BotMode.GRAMMAR: "Send me any grammar topic (e.g., 'present perfect') and I'll explain it!"
    }
    
    INVALID_MODE_TEXT = (
        "❌ Invalid mode. Available modes:\n"
        "• dictionary\n"
        "• grammar"
    )
    
    def __init__(self, definer: Definer, session_manager: SessionManager):
        self.definer = definer
        self.sessions = session_manager
    
    def _get_session(self, update: Update) -> "UserSession":
        """Get session for current user."""
        return self.sessions.get_session(update.effective_user.id)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        session = self._get_session(update)
        await update.message.reply_text(
            self.WELCOME_TEXT.format(mode=session.get_mode().value),
            parse_mode="HTML"
        )
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
        session = self._get_session(update)
        await update.message.reply_text(
            self.HELP_TEXT.format(mode=session.get_mode().value),
            parse_mode="HTML"
        )
    
    async def mode(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /mode command."""
        session = self._get_session(update)
        args = context.args
        
        # If no args, show current mode
        if not args:
            current = session.get_mode().value
            await update.message.reply_text(
                f"Current mode: <b>{current}</b>\n\n"
                f"Use /mode &lt;type&gt; to switch (dictionary/grammar)",
                parse_mode="HTML"
            )
            return
        
        # Try to switch mode
        mode_input = args[0].lower()
        try:
            new_mode = BotMode(mode_input)
            session.set_mode(new_mode)
            
            instruction = self.MODE_INSTRUCTIONS[new_mode]
            await update.message.reply_text(
                self.MODE_SWITCHED_TEXT.format(mode=new_mode.value, instruction=instruction),
                parse_mode="HTML"
            )
            
        except ValueError:
            await update.message.reply_text(self.INVALID_MODE_TEXT)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Route message based on current mode."""
        session = self._get_session(update)
        text = update.message.text.strip()
        
        if not text:
            return
        
        # Show typing indicator
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        
        # Route to appropriate handler
        mode = session.get_mode()
        if mode == BotMode.DICTIONARY:
            await self._handle_dictionary(update, text)
        elif mode == BotMode.GRAMMAR:
            await self._handle_grammar(update, text)
    
    async def _handle_dictionary(self, update: Update, word: str) -> None:
        """Handle dictionary definition request."""
        try:
            definition = self.definer.define_word(word)
            
            safe_word = html.escape(word.capitalize())
            safe_definition = html.escape(definition)
            
            response = f"📖 <b>{safe_word}</b>\n\n{safe_definition}"
            await update.message.reply_text(response, parse_mode="HTML")
            
        except Exception as e:
            logger.error(f"Error defining word '{word}': {e}", exc_info=True)
            await update.message.reply_text(
                "❌ Sorry, I couldn't define that word. Please try again."
            )
    
    async def _handle_grammar(self, update: Update, grammar: str) -> None:
        """Handle grammar explanation request."""
        try:
            explanation = self.definer.explain_grammar(grammar)
            
            safe_grammar = html.escape(grammar.capitalize())
            safe_explanation = html.escape(explanation)
            
            response = f"📚 <b>Grammar: {safe_grammar}</b>\n\n{safe_explanation}"
            await update.message.reply_text(response, parse_mode="HTML")
            
        except Exception as e:
            logger.error(f"Error explaining grammar '{grammar}': {e}", exc_info=True)
            await update.message.reply_text(
                "❌ Sorry, I couldn't explain that grammar topic. Please try again."
            )
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors."""
        logger.error(f"Update {update} caused error: {context.error}", exc_info=True)
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "⚠️ An error occurred. Please try again."
            )