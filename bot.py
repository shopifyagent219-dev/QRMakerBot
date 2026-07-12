import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from config import BOT_TOKEN, BOT_NAME, COMMANDS
from handlers.qr_handlers import (
    start_command,
    help_command,
    text_qr_command,
    url_qr_command,
    wifi_qr_command,
    contact_qr_command,
    read_qr_command,
    handle_message,
    handle_callback,
    handle_wifi_input,
    handle_contact_input
)
from handlers.qr_handlers import WAITING_WIFI_SSID, WAITING_WIFI_PASSWORD, WAITING_CONTACT_NAME, WAITING_CONTACT_PHONE

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Start the bot"""
    print(f"🚀 Starting {BOT_NAME}...")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("textqr", text_qr_command))
    application.add_handler(CommandHandler("urlqr", url_qr_command))
    application.add_handler(CommandHandler("wifisettings", wifi_qr_command))
    application.add_handler(CommandHandler("contact", contact_qr_command))
    application.add_handler(CommandHandler("readqr", read_qr_command))
    
    # Add callback query handler for inline buttons
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Add conversation handlers for WiFi
    wifi_conv = ConversationHandler(
        entry_points=[CommandHandler("wifisettings", wifi_qr_command)],
        states={
            WAITING_WIFI_SSID: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_wifi_input)],
            WAITING_WIFI_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_wifi_input)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: u.message.reply_text("❌ Cancelled."))],
    )
    application.add_handler(wifi_conv)
    
    # Add conversation handlers for Contact
    contact_conv = ConversationHandler(
        entry_points=[CommandHandler("contact", contact_qr_command)],
        states={
            WAITING_CONTACT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_contact_input)],
            WAITING_CONTACT_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_contact_input)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: u.message.reply_text("❌ Cancelled."))],
    )
    application.add_handler(contact_conv)
    
    # Add message handler for text and photos
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, read_qr_command))
    
    # Start the bot
    print(f"✅ {BOT_NAME} is running!")
    print("🤖 Bot is ready to generate QR codes!")
    
    # Start polling
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
