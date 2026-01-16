import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# These will be pulled from your Railway Dashboard
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_GROUP_ID = int(os.getenv('ADMIN_GROUP_ID'))

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

async def handle_inbound(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Forward DMs to the Admin Group"""
    if update.message:
        await context.bot.forward_message(
            chat_id=ADMIN_GROUP_ID,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id
        )

async def handle_outbound(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send admin's reply back to the user"""
    if update.message.reply_to_message and update.message.reply_to_message.forward_from:
        target_user_id = update.message.reply_to_message.forward_from.id
        try:
            await context.bot.send_message(chat_id=target_user_id, text=update.message.text)
        except Exception as e:
            await update.message.reply_text(f"Error: {e}")
    else:
        await update.message.reply_text("❌ Reply failed: Could not find original User ID.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Inbound: Private messages -> Group
    application.add_handler(MessageHandler(filters.ChatType.PRIVATE & (~filters.COMMAND), handle_inbound))
    
    # Outbound: Reply in Group -> User
    application.add_handler(MessageHandler(filters.Chat(ADMIN_GROUP_ID) & filters.REPLY, handle_outbound))
    
    application.run_polling()