import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN found! Please set TELEGRAM_BOT_TOKEN environment variable.")

# Bot Settings
BOT_NAME = "QR Magic Bot"
BOT_DESCRIPTION = "Generate QR codes for text, URLs, WiFi, vCards, and more!"

# QR Code Settings
QR_DEFAULT_SIZE = 300
QR_DEFAULT_BORDER = 4

# Supported commands and their descriptions
COMMANDS = {
    'start': 'Start the bot and see welcome message',
    'help': 'Get help on how to use the bot',
    'textqr': 'Generate QR code from text',
    'urlqr': 'Generate QR code from URL',
    'wifisettings': 'Generate QR code for WiFi login',
    'contact': 'Generate QR code for contact (vCard)',
    'readqr': 'Read QR code from an image'
}

# Maximum allowed input length
MAX_TEXT_LENGTH = 1000
