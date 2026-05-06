import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from genius_humanizer import GeniusHumanizer
import config
import check_env

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Global Humanizer Instance
humanizer = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message when the command /start is issued."""
    user = update.effective_user.first_name
    await update.message.reply_text(
        f"👋 Welcome {user} to Genius Humanizer Bot!\n\n"
        "Sending 'AI-generated' text? I will rewrite it to be 100% Human-like.\n"
        "Just send me any text and wait for the magic! 🧠✨"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Just send me text, and I'll humanize it. No commands needed!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Humanizes the received text."""
    text = update.message.text
    
    if not text:
        return

    # Notify user that processing started
    processing_msg = await update.message.reply_text("🧠 Humanizing... (This requires deep thinking)")
    
    try:
        # Run the CPU-bound task in a separate thread to not block the bot
        loop = asyncio.get_running_loop()
        humanized_text = await loop.run_in_executor(None, humanizer.humanize, text)
        
        # Edit the status message with the result or send new message?
        # Editing is cleaner but if text is long, might need splitting or new message.
        # Let's send a new message for clarity.
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=processing_msg.message_id)
        
        # Split text if too long (Telegram limit 4096)
        if len(humanized_text) > 4000:
            for x in range(0, len(humanized_text), 4000):
                await update.message.reply_text(humanized_text[x:x+4000])
        else:
            await update.message.reply_text(humanized_text)

    except Exception as e:
        logger.error(f"Error occurred: {e}")
        await processing_msg.edit_text(f"❌ An error occurred: {str(e)}")

def main():
    global humanizer
    # Initialize Humanizer once on startup
    print("⏳ Loading Genius Model... (may take almost 30s)")
    try:
        humanizer = GeniusHumanizer()
        print("✅ Model Loaded! Bot is starting...")
    except Exception as e:
        print(f"❌ Critical Error loading model: {e}")
        return

    if config.BOT_TOKEN == "YOUR_TOKEN_HERE":
        print("❌ ERROR: Please set your BOT_TOKEN in config.py")
        return

    # Create the Application
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    # Run the bot
    print("🤖 Bot is running! Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == '__main__':
    main()
