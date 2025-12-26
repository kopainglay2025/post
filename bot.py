import asyncio
import logging
from pyrogram import Client, filters, types
from pyrogram.errors import FloodWait

# ====== Config (STRICTLY PRIVATE) ======
# Use the credentials from your code, but remember to reset them after use!
API_ID = 27333186       
API_HASH = "434cc8a51ba304ea539c19de850ba2b3"
BOT_TOKEN = "5681598508:AAGbT8p5aun5ehww22bfMMrEhSnN1lIZGQU"

CHANNEL_ID = "@MKSMOVIECHANNEL" 
OLD_LINK = "https://t.me/IU_MM_BOT"
NEW_LINK = "https://t.me/RMC_Delivery_Servicebot"

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Client("mks_bot_updater", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def replace_buttons(reply_markup: types.InlineKeyboardMarkup):
    """Scan and replace links in the movie post buttons."""
    new_keyboard = []
    changed = False
    for row in reply_markup.inline_keyboard:
        new_row = []
        for button in row:
            # Check if the button has a URL and if it matches the target OLD_LINK
            if button.url and OLD_LINK in button.url:
                new_url = button.url.replace(OLD_LINK, NEW_LINK)
                new_row.append(types.InlineKeyboardButton(text=button.text, url=new_url))
                changed = True
            else:
                new_row.append(button)
        new_keyboard.append(new_row)
    return types.InlineKeyboardMarkup(new_keyboard), changed

async def update_existing_posts():
    """Iterates through the channel to fix existing movie buttons."""
    print("--- Starting History Update for MKS Movie Channel ---")
    count = 0
    try:
        async for message in app.get_chat_history(CHANNEL_ID, limit=500):
            if message.reply_markup:
                new_markup, changed = replace_buttons(message.reply_markup)
                if changed:
                    try:
                        await message.edit_reply_markup(reply_markup=new_markup)
                        count += 1
                        logging.info(f"Updated Post ID: {message.message_id}")
                        await asyncio.sleep(1.5)  # Delay to prevent Telegram Flood limits
                    except FloodWait as e:
                        logging.warning(f"Flood limit hit. Sleeping for {e.value}s")
                        await asyncio.sleep(e.value)
                    except Exception as e:
                        logging.error(f"Failed to edit {message.message_id}: {e}")
        print(f"--- History Update Complete. Total posts fixed: {count} ---")
    except Exception as e:
        logging.error(f"Chat history access error: {e}")

@app.on_message(filters.chat(CHANNEL_ID) & filters.incoming)
async def monitor_new_posts(client, message):
    """Automatically fixes buttons on any new movie posters added to the channel."""
    if message.reply_markup:
        new_markup, changed = replace_buttons(message.reply_markup)
        if changed:
            try:
                # Give the original poster a moment to finish the upload
                await asyncio.sleep(1) 
                await message.edit_reply_markup(reply_markup=new_markup)
                logging.info(f"Auto-fixed new post: {message.message_id}")
            except Exception as e:
                logging.error(f"Auto-fix failed for {message.message_id}: {e}")

async def main():
    async with app:
        # Start scanning history in the background
        asyncio.create_task(update_existing_posts())
        print("Bot is active. Monitoring for new movie uploads...")
        await asyncio.Future()

if __name__ == "__main__":
    app.run(main())
