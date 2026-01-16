import os
import logging
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters
from telegram.constants import ParseMode

# Railway o'zgaruvchilari (Variables)
# BOT_TOKEN = os.getenv('BOT_TOKEN')
# ADMIN_GROUP_ID = int(os.getenv('ADMIN_GROUP_ID'))
BOT_TOKEN = "8273590083:AAHBR1nPZipQEfLwjlEa8qVVmHQ8aIS-ClA"
ADMIN_GROUP_ID = -1003539723068

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi botni boshlaganda ko'rinadigan salomlashish xabari"""
    user_name = update.effective_user.first_name
    welcome_text = (
        f"<b>Assalomu alaykum, {user_name}!</b>\n\n"
        "Siz bu yerda o'z savollaringiz yoki murojaatlaringizni qoldirishingiz mumkin. "
        "Xabaringizni yozib qoldiring, adminlarimiz tez orada javob berishadi.\n\n"
        "<i>Eslatma: Sizning shaxsingiz adminlar guruhida xavfsiz saqlanadi.</i>"
    )
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.HTML)

async def handle_inbound(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi xabarini guruhga yuborish"""
    if not update.message or not update.message.text:
        return

    user = update.effective_user
    user_text = update.message.text
    
    ticket_ui = (
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>👤 Kimdan:</b> {user.mention_html()}\n"
        f"<b>🆔 ID:</b> <code>{user.id}</code>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>💬 Xabar:</b>\n"
        f"{user_text}"
    )

    await context.bot.send_message(
        chat_id=ADMIN_GROUP_ID,
        text=ticket_ui,
        parse_mode=ParseMode.HTML
    )
    # Foydalanuvchiga xabar yetkazilgani haqida bildirishnoma
    await update.message.reply_text("✅ <i>Xabaringiz adminga yetkazildi. Iltimos, javobni kuting.</i>", parse_mode=ParseMode.HTML)

async def handle_outbound(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin javobini foydalanuvchiga qaytarish"""
    if not update.message.reply_to_message or not update.message.reply_to_message.from_user.is_bot:
        return

    parent_text = update.message.reply_to_message.text
    match = re.search(r"ID:\s(\d+)", parent_text)
    
    if match:
        user_id = int(match.group(1))
        admin_reply = update.message.text
        
        try:
            user_ui = (
                f"{admin_reply}"
            )
            
            await context.bot.send_message(chat_id=user_id, text=user_ui, parse_mode=ParseMode.HTML)
            await update.message.reply_text("✅ <b>Javob yuborildi.</b>", parse_mode=ParseMode.HTML)
            
        except Exception as e:
            await update.message.reply_text(f"❌ <b>Xatolik:</b> {e}", parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text("⚠️ <b>Xato:</b> ID topilmadi.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Komandalar
    application.add_handler(CommandHandler("start", start))
    
    # Shaxsiy xabarlar (DMs)
    application.add_handler(MessageHandler(filters.ChatType.PRIVATE & (~filters.COMMAND), handle_inbound))
    
    # Guruhdagi javoblar (Replies)
    application.add_handler(MessageHandler(filters.Chat(ADMIN_GROUP_ID) & filters.REPLY, handle_outbound))
    
    application.run_polling()