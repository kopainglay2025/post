import asyncio
import logging
from pyrogram import Client, filters, types
from pyrogram.errors import FloodWait

# ====== Config (Keep these private!) ======
API_ID = 27333186       
API_HASH = "434cc8a51ba304ea539c19de850ba2b3"
BOT_TOKEN = "5681598508:AAGbT8p5aun5ehww22bfMMrEhSnN1lIZGQU"

CHANNEL_ID = "@MKSMOVIECHANNEL" 
OLD_LINK = "https://t.me/IU_MM_BOT"
NEW_LINK = "https://t.me/RMC_Delivery_Servicebot"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Client("auto_edit_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def replace_buttons(reply_markup: types.InlineKeyboardMarkup):
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

async def update_all_existing_messages():
    print("--- Starting History Update ---")
    async for message in app.get_chat_history(CHANNEL_ID, limit=1000):
        if message.reply_markup:
            new_markup, changed = replace_buttons(message.reply_markup)
            if changed:
                try:
                    await message.edit_reply_markup(reply_markup=new_markup)
                    logging.info(f"Updated Message ID: {message.message_id}")
                    await asyncio.sleep(2) # Safer delay for bulk edits
                except FloodWait as e:
                    print(f"Waiting {e.value} seconds due to flood limit...")
                    await asyncio.sleep(e.value)
                except Exception as e:
                    logging.error(f"Error on {message.message_id}: {e}")

@app.on_message(filters.chat(CHANNEL_ID) & filters.incoming)
async def auto_update_new_message(client, message):
    if message.reply_markup:
        new_markup, changed = replace_buttons(message.reply_markup)
        if changed:
            try:
                await message.edit_reply_markup(reply_markup=new_markup)
                logging.info(f"Auto-updated new message: {message.message_id}")
            except Exception as e:
                logging.error(f"Failed to auto-update: {e}")

async def main():
    async with app:
        # Run history update in the background so the bot can start monitoring immediately
        asyncio.create_task(update_all_existing_messages())
        print("Bot is monitoring new messages and updating history...")
        await asyncio.Future()

if __name__ == "__main__":
    app.run(main())
