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
START_ID = 25
END_ID = 1415

# Logging setup
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Client("mks_bot_updater", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def replace_buttons(reply_markup: types.InlineKeyboardMarkup):
    """
    Carefully reconstructs the keyboard markup to ensure all buttons 
    are preserved while updating specific URLs.
    """
    new_keyboard = []
    changed = False

    for row in reply_markup.inline_keyboard:
        new_row = []
        for button in row:
            # Handle URL buttons
            if button.url:
                if OLD_LINK in button.url:
                    new_url = button.url.replace(OLD_LINK, NEW_LINK)
                    changed = True
                else:
                    new_url = button.url
                
                new_row.append(
                    types.InlineKeyboardButton(
                        text=button.text,
                        url=new_url
                    )
                )
            # Handle Callback buttons (important to keep these working!)
            elif button.callback_data:
                new_row.append(
                    types.InlineKeyboardButton(
                        text=button.text,
                        callback_data=button.callback_data
                    )
                )
            # Handle Switch Inline buttons if they exist
            elif button.switch_inline_query is not None:
                new_row.append(
                    types.InlineKeyboardButton(
                        text=button.text,
                        switch_inline_query=button.switch_inline_query
                    )
                )
            # Fallback for other button types
            else:
                new_row.append(button)

        new_keyboard.append(new_row)

    return types.InlineKeyboardMarkup(new_keyboard), changed

async def update_message(message_id: int):
    """Updates the reply markup of a single message."""
    try:
        message = await app.get_messages(CHANNEL_ID, message_id)
        
        # Check if message exists and has buttons
        if message and message.reply_markup:
            new_markup, changed = replace_buttons(message.reply_markup)
            
            if changed:
                try:
                    await message.edit_reply_markup(reply_markup=new_markup)
                    logging.info(f"✅ Updated message {message_id}")
                except FloodWait as e:
                    logging.warning(f"⏳ Flood wait {e.value}s. Sleeping...")
                    await asyncio.sleep(e.value)
                    # Retry once after flood wait
                    await message.edit_reply_markup(reply_markup=new_markup)
                except RPCError as e:
                    logging.error(f"❌ Failed to edit {message_id}: {e}")
            else:
                logging.info(f"ℹ️ No changes needed for message {message_id}")
        else:
            logging.info(f"❓ Message {message_id} has no markup or doesn't exist")
            
    except RPCError as e:
        logging.error(f"⚠️ Error fetching message {message_id}: {e}")

async def main():
    async with app:
        logging.info(f"Starting update from {START_ID} to {END_ID}...")
        for message_id in range(START_ID, END_ID + 1):
            await update_message(message_id)
            # Increased delay to be safer with Telegram's API limits
            await asyncio.sleep(2.0) 
            
        logging.info("Task completed successfully.")

if __name__ == "__main__":
    app.run(main())
