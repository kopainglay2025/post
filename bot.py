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
    Button တိုင်းကို ပတ်စစ်ပြီး URL အဟောင်းပါတဲ့ Button မှန်သမျှကို 
    Link အသစ်နဲ့ အစားထိုးပေးပါမည်။
    """
    new_keyboard = []
    any_button_changed = False

    for row in reply_markup.inline_keyboard:
        new_row = []
        for button in row:
            # URL button ဖြစ်ပါက စစ်ဆေးမည်
            if button.url:
                if OLD_LINK in button.url:
                    new_url = button.url.replace(OLD_LINK, NEW_LINK)
                    any_button_changed = True # အနည်းဆုံး Button တစ်ခု ပြောင်းလဲမှုရှိကြောင်း မှတ်သားမည်
                else:
                    new_url = button.url
                
                new_row.append(
                    types.InlineKeyboardButton(
                        text=button.text,
                        url=new_url
                    )
                )
            # Callback buttons များကို မပျက်အောင် ပြန်ထည့်ပေးမည်
            elif button.callback_data:
                new_row.append(
                    types.InlineKeyboardButton(
                        text=button.text,
                        callback_data=button.callback_data
                    )
                )
            # Switch Inline buttons များရှိပါက ပြန်ထည့်ပေးမည်
            elif button.switch_inline_query is not None:
                new_row.append(
                    types.InlineKeyboardButton(
                        text=button.text,
                        switch_inline_query=button.switch_inline_query
                    )
                )
            # အခြား button အမျိုးအစားများအတွက်
            else:
                new_row.append(button)

        new_keyboard.append(new_row)

    return types.InlineKeyboardMarkup(new_keyboard), any_button_changed

async def update_message(message_id: int):
    """မက်ဆေ့ချ်တစ်ခုချင်းစီကို Fetch လုပ်ပြီး Button များကို update လုပ်ပေးမည်။"""
    try:
        message = await app.get_messages(CHANNEL_ID, message_id)
        
        # မက်ဆေ့ချ်ရှိပြီး Button များပါဝင်မှသာ လုပ်ဆောင်မည်
        if message and message.reply_markup:
            new_markup, changed = replace_buttons(message.reply_markup)
            
            # ပြင်ဆင်ရန်လိုအပ်သော Button အနည်းဆုံးတစ်ခုတွေ့မှသာ edit လုပ်မည်
            if changed:
                try:
                    await message.edit_reply_markup(reply_markup=new_markup)
                    logging.info(f"✅ Message {message_id} ကို update လုပ်ပြီးပါပြီ။")
                except FloodWait as e:
                    logging.warning(f"⏳ Flood wait {e.value}s ဖြစ်နေသဖြင့် ခဏစောင့်ပါမည်။")
                    await asyncio.sleep(e.value)
                    await message.edit_reply_markup(reply_markup=new_markup)
                except RPCError as e:
                    logging.error(f"❌ Message {message_id} ကို edit လုပ်၍မရပါ- {e}")
            else:
                logging.info(f"ℹ️ Message {message_id} တွင် ပြင်ဆင်ရန် Link အဟောင်း မတွေ့ပါ။")
        else:
            logging.info(f"❓ Message {message_id} တွင် Button မရှိပါ သို့မဟုတ် မက်ဆေ့ချ် မရှိပါ။")
            
    except RPCError as e:
        logging.error(f"⚠️ Message {message_id} ကို fetch လုပ်စဉ် အမှားရှိခဲ့သည်- {e}")

async def main():
    async with app:
        logging.info(f"ID {START_ID} မှ {END_ID} အထိ စတင်လုပ်ဆောင်နေပါပြီ...")
        for message_id in range(START_ID, END_ID + 1):
            await update_message(message_id)
            # API block မဖြစ်စေရန် ၂ စက္ကန့် delay ထားခြင်း
            await asyncio.sleep(2.0) 
            
        logging.info("လုပ်ငန်းစဉ်အားလုံး ပြီးဆုံးပါပြီ။")

if __name__ == "__main__":
    app.run(main())
