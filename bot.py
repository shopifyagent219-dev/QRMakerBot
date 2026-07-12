import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get token
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set!")

# Simple QR generator fallback if imports fail
try:
    import qrcode
    import io
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False
    logger.error("qrcode module not available")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Welcome {user.first_name}!\n"
        f"I am QR Magic Bot, your QR code generator.\n\n"
        f"📝 Send me any text to generate a QR code!\n"
        f"🌐 Or use /urlqr [URL] for URL QR codes\n"
        f"📶 Use /wifisettings for WiFi QR codes\n"
        f"👤 Use /contact for contact QR codes\n"
        f"📷 Send me an image with QR code to read it\n\n"
        f"🔧 Use /help for more commands"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await update.message.reply_text(
        "🆘 *Available Commands:*\n\n"
        "/start - Start the bot\n"
        "/help - Show this help\n"
        "/textqr [text] - Generate QR from text\n"
        "/urlqr [url] - Generate QR from URL\n"
        "/wifisettings - Generate WiFi QR\n"
        "/contact - Generate contact QR\n"
        "/readqr - Read QR from image\n\n"
        "💡 Or just send me any text!"
    )

async def text_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate QR from text"""
    if not QR_AVAILABLE:
        await update.message.reply_text("❌ QR generation is not available. Please contact the administrator.")
        return
        
    text = ' '.join(context.args) if context.args else None
    if not text:
        await update.message.reply_text("📝 Please provide text. Example: /textqr Hello World")
        return
    
    try:
        await update.message.reply_text("⏳ Generating QR code...")
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        await update.message.reply_photo(
            photo=img_bytes,
            caption=f"✅ QR Code for: `{text[:50]}{'...' if len(text) > 50 else ''}`"
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ Failed to generate QR code. Please try again.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages"""
    if not QR_AVAILABLE:
        await update.message.reply_text("❌ QR generation is not available.")
        return
        
    text = update.message.text
    if len(text) > 500:
        await update.message.reply_text("❌ Text too long! Maximum 500 characters.")
        return
    
    try:
        await update.message.reply_text("⏳ Generating QR code...")
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        await update.message.reply_photo(
            photo=img_bytes,
            caption=f"✅ QR Code generated!"
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ Failed to generate QR code. Please try again.")

def main():
    """Start the bot"""
    print(f"🚀 Starting QR Magic Bot...")
    print(f"📡 Using token: {BOT_TOKEN[:10]}...")
    
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("textqr", text_qr))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Start the bot
        print(f"✅ Bot is running!")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == '__main__':
    main()
