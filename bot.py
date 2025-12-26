from pyrogram import Client, filters, types
import asyncio
import logging
from datetime import datetime

# ====== Config ======
API_ID = 27333186      # သင့် API ID
API_HASH = "434cc8a51ba304ea539c19de850ba2b3"
BOT_TOKEN = "7941502127:AAHoM2MnlScueLMzv44nnYFZr9AlaW4HF7U"

CHANNEL_ID = "-1001949716878"  # Channel username or ID
OLD_LINK = "https://t.me/IU_MM_BOT"
NEW_LINK = "https://t.me/RMC_Delivery_Servicebot"

LOG_FILE = "button_update_log.txt"  # log file path

# ====================

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Client("auto_edit_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def replace_buttons(reply_markup: types.InlineKeyboardMarkup):
    """Inline buttons link replace လုပ်ပြီး ပြန် return"""
    new_keyboard = []
    changed = False
    for row in reply_markup.inline_keyboard:
        new_row = []
        for button in row:
            if button.url and OLD_LINK in button.url:
                new_url = button.url.replace(OLD_LINK, NEW_LINK)
                new_row.append(types.InlineKeyboardButton(text=button.text, url=new_url))
                changed = True
            else:
                new_row.append(button)
        new_keyboard.append(new_row)
    return types.InlineKeyboardMarkup(new_keyboard), changed

# ======= Update existing messages with pagination =======
async def update_all_existing_messages():
    last_message_id = 0
    while True:
        messages = await app.get_chat_history(CHANNEL_ID, limit=100, offset_id=last_message_id)
        if not messages:
            break
        for message in messages:
            if message.reply_markup:
                new_markup, changed = replace_buttons(message.reply_markup)
                if changed:
                    try:
                        await message.edit_reply_markup(reply_markup=new_markup)
                        log_msg = f"[EXISTING UPDATED] Message ID: {message.message_id}"
                        print(log_msg)
                        logging.info(log_msg)
                    except Exception as e:
                        err_msg = f"[FAILED] Message ID: {message.message_id} - {e}"
                        print(err_msg)
                        logging.error(err_msg)
        last_message_id = messages[-1].message_id

# ======= Handler for new messages =======
@app.on_message(filters.channel & (filters.text | filters.photo | filters.video))
async def auto_update_new_message(client, message):
    if message.reply_markup:
        new_markup, changed = replace_buttons(message.reply_markup)
        if changed:
            try:
                await message.edit_reply_markup(reply_markup=new_markup)
                log_msg = f"[NEW UPDATED] Message ID: {message.message_id}"
                print(log_msg)
                logging.info(log_msg)
            except Exception as e:
                err_msg = f"[FAILED] Message ID: {message.message_id} - {e}"
                print(err_msg)
                logging.error(err_msg)

# ======= Run bot =======
async def main():
    async with app:
        print("Updating all existing messages...")
        await update_all_existing_messages()
        print("Bot is now monitoring new messages...")
        await asyncio.Future()  # Keep running

if __name__ == "__main__":
    asyncio.run(main())
