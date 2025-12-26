from pyrogram import Client, filters, types
import logging
import asyncio

# ====== Config ======
API_ID = 27333186       # သင့် API ID
API_HASH = "434cc8a51ba304ea539c19de850ba2b3"
BOT_TOKEN = "7941502127:AAHoM2MnlScueLMzv44nnYFZr9AlaW4HF7U"

CHANNEL_USERNAME = "@MKSMOVIECHANNEL"  # Must include @
OLD_LINK = "https://t.me/IU_MM_BOT"
NEW_LINK = "https://t.me/RMC_Delivery_Servicebot"

LOG_FILE = "button_update_log.txt"

# ====================

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Client("auto_edit_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ======= Replace buttons function =======
def replace_buttons(reply_markup: types.InlineKeyboardMarkup):
    """Replace OLD_LINK with NEW_LINK in all buttons"""
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

# ======= Handler for new messages =======
@app.on_message(filters.channel & (filters.text | filters.photo | filters.video | filters.document))
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

# ======= Run Bot =======
async def main():
    async with app:
        print("Bot is now monitoring new messages...")
        await asyncio.Future()  # Keep running

if __name__ == "__main__":
    asyncio.run(main())
