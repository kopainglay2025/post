import asyncio
import logging
from pyrogram import Client, types
from pyrogram.errors import FloodWait, RPCError

# ====== Config ======
API_ID = 27333186
API_HASH = "434cc8a51ba304ea539c19de850ba2b3"
BOT_TOKEN = "6482888257:AAFycxg9uulw_KBbdvL_WRHlAayElZZyz7o"
CHANNEL_ID = "@applemyanmar"
#OLD_LINK = "https://t.me/TM_Uploadbot"
#NEW_LINK = "https://t.me/Domo_Uploadbot"
START_ID = 25
END_ID = 1415

# Logging setup
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Client("mks_bot_updater", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

from urllib.parse import urlparse

OLD_BOT = "TM_Uploadbot"
NEW_BOT = "Domo_Uploadbot"

def replace_buttons(reply_markup: types.InlineKeyboardMarkup):
    new_keyboard = []
    any_update_needed = False

    for row in reply_markup.inline_keyboard:
        new_row = []

        for button in row:
            if button.url:
                parsed = urlparse(button.url)

                # https://t.me/<botname> ကို စစ်
                if parsed.netloc == "t.me":
                    path = parsed.path.lstrip("/")  # TM_Uploadbot or TM_Uploadbot?start=xxx

                    if path.startswith(OLD_BOT):
                        new_url = button.url.replace(OLD_BOT, NEW_BOT)
                        any_update_needed = True
                    else:
                        new_url = button.url
                else:
                    new_url = button.url

                new_row.append(
                    types.InlineKeyboardButton(
                        text=button.text,
                        url=new_url
                    )
                )

            elif button.callback_data:
                new_row.append(
                    types.InlineKeyboardButton(
                        text=button.text,
                        callback_data=button.callback_data
                    )
                )

            elif button.switch_inline_query is not None:
                new_row.append(
                    types.InlineKeyboardButton(
                        text=button.text,
                        switch_inline_query=button.switch_inline_query
                    )
                )
            else:
                new_row.append(button)

        new_keyboard.append(new_row)

    return types.InlineKeyboardMarkup(new_keyboard), any_update_needed

async def update_message(message_id: int):
    """မက်ဆေ့ချ်တစ်ခုချင်းစီကို Fetch လုပ်ပြီး Button များကို update လုပ်ပေးမည်။"""
    try:
        message = await app.get_messages(CHANNEL_ID, message_id)
        
        if message and message.reply_markup:
            new_markup, needs_update = replace_buttons(message.reply_markup)
            
            # Button တစ်ခုချင်းစီကို စစ်ဆေးပြီး Link အဟောင်း ကျန်နေသေးမှသာ Edit လုပ်မည်
            if needs_update:
                try:
                    await message.edit_reply_markup(reply_markup=new_markup)
                    logging.info(f"✅ Message {message_id} ရှိ Button များကို Update လုပ်ပြီးပါပြီ။")
                except FloodWait as e:
                    logging.warning(f"⏳ Flood wait {e.value}s ဖြစ်နေသဖြင့် ခဏစောင့်ပါမည်။")
                    await asyncio.sleep(e.value)
                    await message.edit_reply_markup(reply_markup=new_markup)
                except RPCError as e:
                    logging.error(f"❌ Message {message_id} ကို edit လုပ်၍မရပါ- {e}")
            else:
                logging.info(f"ℹ️ Message {message_id} ရှိ Button များသည် Link အသစ်ဖြစ်နေပြီးသား ဖြစ်သည်။")
        else:
            logging.info(f"❓ Message {message_id} တွင် Button မရှိပါ။")
            
    except RPCError as e:
        logging.error(f"⚠️ Message {message_id} ကို fetch လုပ်စဉ် အမှားရှိခဲ့သည်- {e}")

async def main():
    async with app:
        logging.info(f"ID {START_ID} မှ {END_ID} အထိ စစ်ဆေးနေပါပြီ...")
        for message_id in range(START_ID, END_ID + 1):
            await update_message(message_id)
            # API Limit မမိစေရန်
            await asyncio.sleep(1.5) 
            
        logging.info("လုပ်ငန်းစဉ်အားလုံး ပြီးဆုံးပါပြီ။")

if __name__ == "__main__":
    app.run(main())
