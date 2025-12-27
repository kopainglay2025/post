import asyncio
import logging
from pyrogram import Client, types
from pyrogram.errors import FloodWait, RPCError

# ====== Config ======
API_ID = 27333186
API_HASH = "434cc8a51ba304ea539c19de850ba2b3"
BOT_TOKEN = "6482888257:AAFycxg9uulw_KBbdvL_WRHlAayElZZyz7o"
CHANNEL_ID = "@applemyanmar"
OLD_LINK = "https://t.me/TM_Uploadbot"
NEW_LINK = "https://t.me/Domo_Uploadbot"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Client("mks_bot_ddhjiupdater", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def replace_buttons(reply_markup: types.InlineKeyboardMarkup):
    """Replace old links with new ones in button markup."""
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

async def update_message(message_id: int):
    """Update a single channel message by ID."""
    try:
        message = await app.get_messages(CHANNEL_ID, message_id)
        if message.reply_markup:
            new_markup, changed = replace_buttons(message.reply_markup)
            if changed:
                try:
                    await message.edit_reply_markup(reply_markup=new_markup)
                    logging.info(f"Updated message {message_id}")
                except FloodWait as e:
                    logging.warning(f"Flood wait {e.value}s for message {message_id}")
                    await asyncio.sleep(e.value)
                except RPCError as e:
                    logging.error(f"Failed to edit message {message_id}: {e}")
            else:
                logging.info(f"No buttons to update in message {message_id}")
        else:
            logging.info(f"Message {message_id} has no buttons")
    except RPCError as e:
        logging.error(f"Failed to fetch message {message_id}: {e}")

async def main():
    async with app:
        start_id = 1
        end_id = 1415
        for message_id in range(start_id, end_id + 1):
            await update_message(message_id)
            await asyncio.sleep(1.5)  # small delay to avoid flood limits
        print(f"Finished updating messages {start_id} to {end_id}")

if __name__ == "__main__":
    app.run(main())
