import asyncio
import logging
from pyrogram import Client, types
from pyrogram.errors import FloodWait, RPCError

# ================= CONFIG =================
API_ID = 27333186
API_HASH = "434cc8a51ba304ea539c19de850ba2b3"
BOT_TOKEN = "6482888257:AAFycxg9uulw_KBbdvL_WRHlAayElZZyz7o"

CHANNEL_ID = "@applemyanmar"

OLD_LINK = "https://t.me/TM_Uploadbot"
NEW_LINK = "https://t.me/Domo_Uploadbot"

START_ID = 25
END_ID = 1415

SLEEP_TIME = 1.5
# ==========================================

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Client(
    "mks_bot_updater",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# =====================================================
# Replace ALL buttons (force update – no skip logic)
# =====================================================
def replace_buttons(reply_markup: types.InlineKeyboardMarkup):
    new_keyboard = []

    for row in reply_markup.inline_keyboard:
        new_row = []
        for button in row:

            # -------- URL BUTTON --------
            if button.url:
                new_url = button.url.replace(OLD_LINK, NEW_LINK)
                new_row.append(
                    types.InlineKeyboardButton(
                        text=button.text,
                        url=new_url
                    )
                )

            # -------- CALLBACK BUTTON --------
            elif button.callback_data:
                new_row.append(
                    types.InlineKeyboardButton(
                        text=button.text,
                        callback_data=button.callback_data
                    )
                )

            # -------- INLINE SWITCH --------
            elif button.switch_inline_query is not None:
                new_row.append(
                    types.InlineKeyboardButton(
                        text=button.text,
                        switch_inline_query=button.switch_inline_query
                    )
                )

            # -------- UNKNOWN TYPE --------
            else:
                new_row.append(button)

        new_keyboard.append(new_row)

    return types.InlineKeyboardMarkup(new_keyboard)


# =====================================================
# Update single message
# =====================================================
async def update_message(message_id: int):
    try:
        message = await app.get_messages(CHANNEL_ID, message_id)

        if not message:
            logging.info(f"❓ Message {message_id} မရှိပါ။")
            return

        if not message.reply_markup:
            logging.info(f"ℹ️ Message {message_id} တွင် Button မရှိပါ။")
            return

        new_markup = replace_buttons(message.reply_markup)

        try:
            await message.edit_reply_markup(reply_markup=new_markup)
            logging.info(f"✅ Message {message_id} Button များကို Update လုပ်ပြီးပါပြီ။")

        except FloodWait as e:
            logging.warning(f"⏳ FloodWait {e.value}s - စောင့်ပါမည်")
            await asyncio.sleep(e.value)
            await message.edit_reply_markup(reply_markup=new_markup)

        except RPCError as e:
            logging.error(f"❌ Message {message_id} edit မရပါ: {e}")

    except RPCError as e:
        logging.error(f"⚠️ Message {message_id} fetch error: {e}")


# =====================================================
# Main loop
# =====================================================
async def main():
    async with app:
        logging.info(f"🔎 Message ID {START_ID} မှ {END_ID} အထိ စစ်ဆေးနေပါပြီ...")

        for message_id in range(START_ID, END_ID + 1):
            await update_message(message_id)
            await asyncio.sleep(SLEEP_TIME)

        logging.info("🎉 Button Update အားလုံး ပြီးဆုံးပါပြီ။")


# =====================================================
# Runner
# =====================================================
if __name__ == "__main__":
    app.run(main())
