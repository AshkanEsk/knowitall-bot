import os
import logging
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from HFAPI import Definer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.ext import CallbackQueryHandler
from telegram import BotCommand

# Environment variables
TOKEN = os.getenv("TOKEN")       # Telegram bot token
HFAPI_TOKEN = os.getenv("HFAPI") # Hugging Face API token

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    # Define inline keyboard
    keyboard = [
        [InlineKeyboardButton("📖 Define a word", callback_data="define")],
        [InlineKeyboardButton("✍️ Explain grammar", callback_data="explain")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_html(
        rf"Hi {user.mention_html()}! 👋\n\n"
        "I can help you with:\n"
        "- Word definitions\n"
        "- Grammar explanations\n\n"
        "Choose an option below:",
        reply_markup=reply_markup
    )


async def set_commands(application):
    await application.bot.set_my_commands([
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Show help"),
        BotCommand("define", "Define a word"),
        BotCommand("explain", "Explain grammar")
    ])

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "define":
        await query.edit_message_text(
            "To define a word, type: `/define your_word`\nExample: `/define apple`",
            parse_mode="Markdown"
        )
    elif query.data == "explain":
        await query.edit_message_text(
            "To explain grammar, type: `/explain topic`\nExample: `/explain present simple`",
            parse_mode="Markdown"
        )
    elif query.data == "help":
        await query.edit_message_text(
            "📖 Use `/help` to see all commands.\n\n"
            "Available:\n- `/start`\n- `/define <word>`\n- `/explain <topic>`\n- `/help`",
            parse_mode="Markdown"
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "📖 *KnowItAll Bot Help*\n\n"
        "Here’s how you can use me:\n"
        "- `/start` → Introduction\n"
        "- `/define <word>` → Get a dictionary-style definition\n"
        "- `/explain <grammar_topic>` → Learn grammar concepts\n"
        "- `/help` → Show this help message\n\n"
        "Example: `/define apple` or `/explain present simple`"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def define(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "Usage: /define <word>\nExample: `/define book`",
            parse_mode="Markdown"
        )
        return

    word = " ".join(context.args)
    definer_instance = context.bot_data.get("definer")

    if not definer_instance:
        await update.message.reply_text("Definition service not available.")
        return

    await update.message.reply_text(f"Looking up definition for '{word}'...")
    try:
        definition = definer_instance.defineWord(word)
        await update.message.reply_text(definition)
    except Exception as e:
        logger.error(f"Error defining word '{word}': {e}")
        await update.message.reply_text("Sorry, I couldn't get a definition.")

async def explain(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "Usage: /explain <grammar_topic>\nExample: `/explain present perfect`",
            parse_mode="Markdown"
        )
        return

    topic = " ".join(context.args)
    definer_instance = context.bot_data.get("definer")

    if not definer_instance:
        await update.message.reply_text("Grammar explanation service not available.")
        return

    await update.message.reply_text(f"Explaining '{topic}'...")
    try:
        explanation = definer_instance.grammarexplainer(topic)
        await update.message.reply_text(explanation)
    except Exception as e:
        logger.error(f"Error explaining grammar '{topic}': {e}")
        await update.message.reply_text("Sorry, I couldn't explain that grammar topic.")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Sorry, I don’t recognize that command. Type `/help` to see what I can do."
    )

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    # Inject Definer instance into bot_data
    application.bot_data["definer"] = Definer(hfapi=HFAPI_TOKEN)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("define", define))
    application.add_handler(CommandHandler("explain", explain))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    # Register bot commands
    #application.post_init(set_commands)

    logger.info("Bot started polling...")
    application.run_polling()

if __name__ == "__main__":
    main()