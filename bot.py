#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import configs
import HFAPI # Assuming HFAPI.py contains the Definer class

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# --- Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"""Hi {user.mention_html()}!
             I can help you with word definitions and grammar explanations.

             To define a word: /define Your_word (e.g., /define define)
             To explain grammar: /explain Grammar_topic (e.g., /explain present simple)""",
        reply_markup=ForceReply(selective=True),
    )

async def define(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Defines a word using the HFAPI.Definer.
    Expects the word to be passed as an argument to the /define command.
    """
    if not context.args:
        await update.message.reply_text(
            "Please provide a word to define. Usage: /define Your_word"
        )
        return

    word = " ".join(context.args)

    definer_instance = context.bot_data.get("definer")
    if not definer_instance:
        logger.error("Definer instance not found in bot_data.")
        await update.message.reply_text(
            "Sorry, the definition service is not available right now. Please try again later."
        )
        return

    await update.message.reply_text(f"Looking up definition for '{word}'...")

    try:
        definition = definer_instance.defineWord(word=word)
        await update.message.reply_text(f"Definition for '{word}':\n\n{definition}")
        await update.message.reply_text("If you need to define another word, please use /define again.")
    except Exception as e:
        logger.error(f"Error defining word '{word}': {e}")
        await update.message.reply_text(
            f"Sorry, I couldn't get a definition for '{word}'. An error occurred. "
            "Please ensure your Hugging Face API token is valid and the model is accessible."
        )

async def explain(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Explains a grammar topic using the HFAPI.Definer.
    Expects the grammar topic to be passed as an argument to the /explain command.
    """
    if not context.args:
        await update.message.reply_text(
            "Please provide a grammar topic to explain. Usage: /explain Grammar_topic"
        )
        return

    grammar_topic = " ".join(context.args)

    definer_instance = context.bot_data.get("definer")
    if not definer_instance:
        logger.error("Definer instance not found in bot_data.")
        await update.message.reply_text(
            "Sorry, the grammar explanation service is not available right now. Please try again later."
        )
        return

    await update.message.reply_text(f"Explaining '{grammar_topic}' grammar...")

    try:
        explanation = definer_instance.grammarexplainer(grammar=grammar_topic)
        await update.message.reply_text(f"Explanation for '{grammar_topic}':\n\n{explanation}")
        await update.message.reply_text("If you need another grammar explanation, please use /explain again.")
    except Exception as e:
        logger.error(f"Error explaining grammar '{grammar_topic}': {e}")
        await update.message.reply_text(
            f"Sorry, I couldn't explain '{grammar_topic}'. An error occurred. "
            "Please ensure your Hugging Face API token is valid and the model is accessible."
        )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message if it's not a command."""
    await update.message.reply_text(update.message.text)


def main() -> None:
    """Start the bot."""
    application = Application.builder().token(configs.TOKEN).build()

    # Instantiate the Definer class ONCE and store it in bot_data
    try:
        application.bot_data["definer"] = HFAPI.Definer(
            hfapi=configs.HFAPI,
            owner=configs.HFOWNER,
            llm=configs.HFLLM
        )
        logger.info("HFAPI.Definer instance created successfully.")
    except Exception as e:
        logger.critical(f"Failed to initialize HFAPI.Definer: {e}. Bot may not function correctly.")
        

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("define", define))
    application.add_handler(CommandHandler("explain", explain))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    logger.info("Bot started polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    logger.info("Bot stopped polling.")


if __name__ == "__main__":
    main()