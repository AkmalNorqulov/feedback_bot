import os
import logging
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode

# Railway o'zgaruvchilari (Variables)
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_GROUP_ID = int(os.getenv('ADMIN_GROUP_ID'))

# Loglarni sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

async def handle_inbound(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi xabarini guruhga chiroyli formatda yuboradi"""
    if not update.message or not update.message.text:
        return

    user = update.effective_user
    user_text = update.message.text
    
    # Guruh uchun chiroyli UI dizayni
    ticket_ui = (
        f"<b>📥 YANGI MUROJAAT</b>\n"
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

async def handle_outbound(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin javobini foydalanuvchiga qaytaradi"""
    # Faqat bot yuborgan xabarga javob berilganda ishlaydi
    if not update.message.reply_to_message or not update.message.reply_to_message.from_user.is_bot:
        return

    parent_text = update.message.reply_to_message.text
    
    # Xabar matnidan ID raqamini qidirib topish
    match = re.search(r"ID:\s(\d+)", parent_text)
    
    if match:
        user_id = int(match.group(1))
        admin_reply = update.message.text
        
        try:
            # Foydalanuvchi ko'radigan UI
            user_ui = (
                f"<b>📩 Qo'llab-quvvatlash xizmatidan javob</b>\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"{admin_reply}"
            )
            
            await context.bot.send_message(
                chat_id=user_id,
                text=user_ui,
                parse_mode=ParseMode.HTML
            )
            
            # Adminga tasdiqlash xabari
            await update.message.reply_text("✅ <b>Xabar yuborildi.</b>", parse_mode=ParseMode.HTML)
            
        except Exception as e:
            await update.message.reply_text(f"❌ <b>Yuborishda xatolik:</b> {e}", parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text("⚠️ <b>Xato:</b> Xabardan foydalanuvchi ID raqami topilmadi.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # 1. Shaxsiy xabarlar -> Guruhga
    application.add_handler(MessageHandler(filters.ChatType.PRIVATE & (~filters.COMMAND), handle_inbound))
    
    # 2. Guruhdagi javob (Reply) -> Foydalanuvchiga
    application.add_handler(MessageHandler(filters.Chat(ADMIN_GROUP_ID) & filters.REPLY, handle_outbound))
    
    print("Bot o'zbek tilida ishga tushdi...")
    application.run_polling()