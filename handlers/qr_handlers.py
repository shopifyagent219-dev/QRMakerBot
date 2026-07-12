import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from utils.qr_generator import QRGenerator
from config import BOT_NAME, COMMANDS, MAX_TEXT_LENGTH

# Setup logging
logger = logging.getLogger(__name__)

# Conversation states
WAITING_WIFI_SSID = 1
WAITING_WIFI_PASSWORD = 2
WAITING_CONTACT_NAME = 3
WAITING_CONTACT_PHONE = 4

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when /start is issued."""
    user = update.effective_user
    welcome_message = (
        f"👋 Welcome {user.first_name}!\n"
        f"I am {BOT_NAME}, your personal QR code generator.\n\n"
        f"✨ I can help you create QR codes for:\n"
        f"• 📝 Text messages\n"
        f"• 🌐 URLs and links\n"
        f"• 📶 WiFi networks\n"
        f"• 👤 Contact information (vCard)\n"
        f"• 📷 Read QR codes from images\n\n"
        f"🔧 Use /help to see all available commands.\n"
        f"🤖 Let's get started!"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("📝 Text QR", callback_data="textqr"),
            InlineKeyboardButton("🌐 URL QR", callback_data="urlqr")
        ],
        [
            InlineKeyboardButton("📶 WiFi QR", callback_data="wifisettings"),
            InlineKeyboardButton("👤 Contact QR", callback_data="contact")
        ],
        [
            InlineKeyboardButton("📷 Read QR", callback_data="readqr"),
            InlineKeyboardButton("❓ Help", callback_data="help")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when /help is issued."""
    help_text = (
        f"🆘 *How to use {BOT_NAME}*\n\n"
        f"Here are all the commands you can use:\n\n"
        f"📌 `/start` - Start the bot\n"
        f"📌 `/help` - Show this help message\n"
        f"📌 `/textqr [text]` - Generate QR from text\n"
        f"   Example: `/textqr Hello World`\n\n"
        f"📌 `/urlqr [url]` - Generate QR from URL\n"
        f"   Example: `/urlqr https://example.com`\n\n"
        f"📌 `/wifisettings` - Generate WiFi QR (interactive)\n"
        f"📌 `/contact` - Generate contact QR (interactive)\n"
        f"📌 `/readqr` - Read QR code from an image\n\n"
        f"💡 *Tips:*\n"
        f"• You can also send any text directly to generate a QR code\n"
        f"• Send an image with a QR code to read it\n"
        f"• Maximum text length is {MAX_TEXT_LENGTH} characters"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def text_qr_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate QR code from text."""
    text = ' '.join(context.args) if context.args else None
    
    if not text:
        await update.message.reply_text(
            "📝 Please provide text to generate a QR code.\n"
            "Example: `/textqr Hello World`"
        )
        return
    
    if len(text) > MAX_TEXT_LENGTH:
        await update.message.reply_text(
            f"❌ Text is too long! Maximum {MAX_TEXT_LENGTH} characters allowed."
        )
        return
    
    await update.message.reply_text("⏳ Generating QR code...")
    
    try:
        qr_file = QRGenerator.generate_text_qr(text)
        await update.message.reply_photo(
            photo=qr_file,
            caption=f"✅ QR Code generated for:\n`{text[:100]}{'...' if len(text) > 100 else ''}`"
        )
    except Exception as e:
        logger.error(f"Error generating QR: {e}")
        await update.message.reply_text("❌ Failed to generate QR code. Please try again.")

async def url_qr_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate QR code from URL."""
    url = ' '.join(context.args) if context.args else None
    
    if not url:
        await update.message.reply_text(
            "🌐 Please provide a URL to generate a QR code.\n"
            "Example: `/urlqr https://example.com`"
        )
        return
    
    # Validate URL
    url_pattern = re.compile(r'^https?://.+')
    if not url_pattern.match(url):
        await update.message.reply_text(
            "❌ Please enter a valid URL starting with http:// or https://"
        )
        return
    
    await update.message.reply_text("⏳ Generating QR code...")
    
    try:
        qr_file = QRGenerator.generate_url_qr(url)
        await update.message.reply_photo(
            photo=qr_file,
            caption=f"✅ QR Code generated for:\n`{url[:100]}{'...' if len(url) > 100 else ''}`"
        )
    except Exception as e:
        logger.error(f"Error generating QR: {e}")
        await update.message.reply_text("❌ Failed to generate QR code. Please try again.")

async def wifi_qr_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start interactive WiFi QR generation."""
    await update.message.reply_text(
        "📶 *WiFi QR Code Generator*\n\n"
        "Please send me the WiFi network name (SSID).\n"
        "Example: `MyWiFiNetwork`\n\n"
        "Type /cancel to cancel."
    )
    return WAITING_WIFI_SSID

async def contact_qr_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start interactive contact QR generation."""
    await update.message.reply_text(
        "👤 *Contact QR Code Generator*\n\n"
        "Please send me the contact's full name.\n"
        "Example: `John Doe`\n\n"
        "Type /cancel to cancel."
    )
    return WAITING_CONTACT_NAME

async def read_qr_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Read QR code from image."""
    if update.message and update.message.photo:
        # User sent a photo
        await update.message.reply_text("📷 Reading QR code from image...")
        
        try:
            # Get the largest photo
            photo_file = await update.message.photo[-1].get_file()
            qr_text = QRGenerator.read_qr_from_image(photo_file)
            
            if qr_text:
                await update.message.reply_text(
                    f"✅ QR Code detected!\n\n"
                    f"📝 Content:\n`{qr_text[:500]}{'...' if len(qr_text) > 500 else ''}`"
                )
            else:
                await update.message.reply_text(
                    "❌ No QR code found in the image.\n"
                    "Please make sure the QR code is clearly visible."
                )
        except Exception as e:
            logger.error(f"Error reading QR: {e}")
            await update.message.reply_text("❌ Failed to read QR code. Please try again.")
    else:
        await update.message.reply_text(
            "📷 Please send me an image containing a QR code.\n"
            "I will read it and tell you what it contains!"
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages that aren't commands."""
    text = update.message.text
    
    # Check if we're in a conversation
    if context.user_data.get('wifi_mode'):
        await handle_wifi_input(update, context)
        return
    elif context.user_data.get('contact_mode'):
        await handle_contact_input(update, context)
        return
    
    # Regular text - generate QR code
    if len(text) > MAX_TEXT_LENGTH:
        await update.message.reply_text(
            f"❌ Text is too long! Maximum {MAX_TEXT_LENGTH} characters allowed."
        )
        return
    
    await update.message.reply_text("⏳ Generating QR code...")
    
    try:
        qr_file = QRGenerator.generate_text_qr(text)
        await update.message.reply_photo(
            photo=qr_file,
            caption=f"✅ QR Code generated for:\n`{text[:100]}{'...' if len(text) > 100 else ''}`"
        )
    except Exception as e:
        logger.error(f"Error generating QR: {e}")
        await update.message.reply_text("❌ Failed to generate QR code. Please try again.")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline keyboard callbacks."""
    query = update.callback_query
    await query.answer()
    
    # Map callback to commands
    command_map = {
        'textqr': text_qr_command,
        'urlqr': url_qr_command,
        'wifisettings': wifi_qr_command,
        'contact': contact_qr_command,
        'readqr': read_qr_command,
        'help': help_command
    }
    
    if query.data in command_map:
        await command_map[query.data](update, context)

async def handle_wifi_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle WiFi conversation input."""
    text = update.message.text
    
    if not context.user_data.get('wifi_ssid'):
        context.user_data['wifi_ssid'] = text
        await update.message.reply_text(
            f"✅ WiFi network set to: `{text}`\n\n"
            "Now please send me the WiFi password.\n\n"
            "Type /cancel to cancel."
        )
        return WAITING_WIFI_PASSWORD
    
    wifi_password = text
    wifi_ssid = context.user_data.pop('wifi_ssid')
    
    await update.message.reply_text("⏳ Generating WiFi QR code...")
    
    try:
        qr_file = QRGenerator.generate_wifi_qr(wifi_ssid, wifi_password)
        await update.message.reply_photo(
            photo=qr_file,
            caption=f"✅ WiFi QR Code generated for:\n📶 `{wifi_ssid}`"
        )
    except Exception as e:
        logger.error(f"Error generating WiFi QR: {e}")
        await update.message.reply_text("❌ Failed to generate WiFi QR code. Please try again.")
    
    return ConversationHandler.END

async def handle_contact_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle contact conversation input."""
    text = update.message.text
    
    if not context.user_data.get('contact_name'):
        context.user_data['contact_name'] = text
        await update.message.reply_text(
            f"✅ Contact name set to: `{text}`\n\n"
            "Now please send me the contact's phone number.\n"
            "Example: `+1234567890`\n\n"
            "Type /cancel to cancel."
        )
        return WAITING_CONTACT_PHONE
    
    phone = text
    name = context.user_data.pop('contact_name')
    
    await update.message.reply_text("⏳ Generating contact QR code...")
    
    try:
        qr_file = QRGenerator.generate_contact_qr(name, phone)
        await update.message.reply_photo(
            photo=qr_file,
            caption=f"✅ Contact QR Code generated for:\n👤 `{name}`"
        )
    except Exception as e:
        logger.error(f"Error generating contact QR: {e}")
        await update.message.reply_text("❌ Failed to generate contact QR code. Please try again.")
    
    return ConversationHandler.END
