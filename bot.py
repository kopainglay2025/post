import asyncio
import logging
from pyrogram import Client, filters, types
from pyrogram.errors import FloodWait

# Config
API_ID = 27333186       
API_HASH = "434cc8a51ba304ea539c19de850ba2b3"
CHANNEL_ID = "@MKSMOVIECHANNEL" 
OLD_LINK = "https://t.me/IU_MM_BOT"
NEW_LINK = "https://t.me/RMC_Delivery_Servicebot"

# Use a session name. No Bot Token.
app = Client("mks_user_updater", api_id=API_ID, api_hash=API_HASH)

def replace_buttons(reply_markup):
    if not reply_markup: return None, False
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

async def update_existing_posts():
    print("--- Starting History Update via User Account ---")
    async for message in app.get_chat_history(CHANNEL_ID, limit=1000):
        if message.reply_markup:
            new_markup, changed = replace_buttons(message.reply_markup)
            if changed:
                try:
                    await app.edit_message_reply_markup(CHANNEL_ID, message.id, reply_markup=new_markup)
                    logging.info(f"Updated: {message.id}")
                    await asyncio.sleep(2) 
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                except Exception as e:
                    logging.error(f"Error {message.id}: {e}")
    print("--- Task Finished ---")

async def main():
    async with app:
        await update_existing_posts()

if __name__ == "__main__":
    app.run(main())
