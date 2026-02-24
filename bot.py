import os
import logging
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, ContextTypes
from HFAPI import Definer

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
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! Send /define <word> to get a definition.",
        reply_markup=ForceReply(selective=True),
    )

async def define(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /define <word>")
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

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    # Inject Definer instance into bot_data
    application.bot_data["definer"] = Definer(hfapi=HFAPI_TOKEN)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("define", define))

    logger.info("Bot started polling...")
    application.run_polling()

if __name__ == "__main__":
    main()