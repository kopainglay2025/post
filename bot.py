import asyncio
import logging
from pyrogram import Client
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ========= CONFIG =========
API_ID = 27333186
API_HASH = "434cc8a51ba304ea539c19de850ba2b3"
BOT_TOKEN = "6482888257:AAFycxg9uulw_KBbdvL_WRHlAayElZZyz7o"

CHANNEL_ID = "@applemyanmar"

OLD_LINK = "https://t.me/TM_Uploadbot"
NEW_LINK = "https://t.me/Domo_Uploadbot"

DELAY = 1.3   # anti flood
LIMIT = 0     # 0 = no limit (full history)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Client(
    "next_level_updater",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ========= BUTTON FIX =========
def rebuild_buttons(markup: InlineKeyboardMarkup):
    changed = False
    keyboard = []

    for row in markup.inline_keyboard:
        new_row = []
        for btn in row:
            if btn.url:
                new_url = btn.url
                if OLD_LINK in new_url:
                    new_url = new_url.replace(OLD_LINK, NEW_LINK)
                    changed = True

                new_row.append(
                    InlineKeyboardButton(
                        text=btn.text,
                        url=new_url
                    )
                )
            else:
                new_row.append(
                    InlineKeyboardButton(
                        text=btn.text,
                        callback_data=btn.callback_data
                    )
                )
        keyboard.append(new_row)

    return InlineKeyboardMarkup(keyboard), changed

# ========= CAPTION / TEXT FIX =========
def replace_text_links(text: str):
    if not text:
        return text, False

    if OLD_LINK in text:
        return text.replace(OLD_LINK, NEW_LINK), True

    return text, False

# ========= MAIN =========
async def run():
    async with app:
        count = 0
        async for msg in app.get_chat_history(CHANNEL_ID, limit=LIMIT):
            try:
                if not msg:
                    continue

                edited = False

                # ---- BUTTONS ----
                if msg.reply_markup:
                    new_markup, btn_changed = rebuild_buttons(msg.reply_markup)
                else:
                    new_markup, btn_changed = None, False

                # ---- TEXT / CAPTION ----
                if msg.caption:
                    new_text, text_changed = replace_text_links(msg.caption)
                elif msg.text:
                    new_text, text_changed = replace_text_links(msg.text)
                else:
                    new_text, text_changed = None, False

                if not (btn_changed or text_changed):
                    continue

                await msg.edit(
                    text=new_text if msg.text else None,
                    caption=new_text if msg.caption else None,
                    reply_markup=new_markup if btn_changed else msg.reply_markup
                )

                count += 1
                logging.info(f"✅ Updated message ID: {msg.id}")

                await asyncio.sleep(DELAY)

            except FloodWait as e:
                logging.warning(f"⏳ FloodWait {e.value}s")
                await asyncio.sleep(e.value)

            except RPCError as e:
                logging.error(f"❌ Message {msg.id} failed: {e}")

        logging.info(f"🎉 Finished! Total updated: {count}")

if __name__ == "__main__":
    app.run(run())
