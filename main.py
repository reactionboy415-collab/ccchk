import logging
import re
import asyncio
import requests
import random
import urllib.parse
import os
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
BOT_TOKEN = "8318488317:AAGGuMfRMqOaGv0ZJfyAedAFRULVHVvy8qI"
ADMIN_ID = 7840042951
ADMIN_HANDLE = "@dev2dex"

logging.basicConfig(level=logging.INFO)

class PirateBotEngine:
    def __init__(self):
        self.session = requests.Session()
        self.ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    def get_bin_info(self, bin_num):
        try:
            response = requests.get(f"https://bins.antipublic.cc/bins/{bin_num[:6]}", timeout=5)
            if response.status_code == 200:
                return response.json()
        except: pass
        return {}

    async def check_cc_api(self, cc_details):
        url = "https://api.chkr.cc/"
        payload = {"data": cc_details, "charge": False}
        headers = {"User-Agent": self.ua, "Content-Type": "application/json"}
        try:
            response = self.session.post(url, json=payload, headers=headers, timeout=25)
            return response.json()
        except: return None

bot_engine = PirateBotEngine()

# --- PROGRESS BAR FUNCTION ---
async def show_progress(message, action_text):
    bars = [
        "▒▒▒▒▒▒▒▒▒▒ 0%", "█▒▒▒▒▒▒▒▒▒ 10%", "██▒▒▒▒▒▒▒▒ 25%", 
        "███▒▒▒▒▒▒▒ 40%", "█████▒▒▒▒▒ 60%", "███████▒▒▒ 85%", 
        "██████████ 100%"
    ]
    temp_msg = await message.reply_text(f"⏳ `{bars[0]}`\n{action_text}")
    for bar in bars[1:]:
        await asyncio.sleep(0.4)
        await temp_msg.edit_text(f"⏳ `{bar}`\n{action_text}")
    return temp_msg

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    prog = await show_progress(update.message, "Please wait, registering your account on DB...")
    
    banner = f"https://placehold.jp/80/000000/ffd700/1200x600.png?text=WELCOME%20{urllib.parse.quote(user.first_name.upper())}"
    text = (f"🎊 WELCOME, {user.first_name}! 🎊\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"🚀 **PIRATEs CHECKER v5.0**\n"
            f"Gateway: `chkr.cc Premium` 🔒\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"📜 Commands:\n"
            f"🔹 `/chk CARD|MM|YY|CVV` - Check CC\n"
            f"🔹 `/gen BIN` - Generate Cards\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"🛠 Dev: {ADMIN_HANDLE}")
    await prog.delete()
    await update.message.reply_photo(photo=banner, caption=text, parse_mode="Markdown")

async def gen_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bin_match = re.search(r'\d{6}', update.message.text)
    if not bin_match: return
    
    prog = await show_progress(update.message, "Fetching BIN data & generating cards...")
    
    bin_num = bin_match.group()
    d = bot_engine.get_bin_info(bin_num)
    
    # Simple generation logic
    cards = []
    for _ in range(10):
        c = bin_num + "".join([str(random.randint(0,9)) for _ in range(10)])
        cards.append(f"`{c}|{random.choice(['01','12'])}|{random.randint(2026,2030)}|{random.randint(100,999)}`")

    res = (
        f"💠 **PIRATEs GENERATOR** ⚡\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏦 **BIN:** `{bin_num}`\n"
        f"🌍 **INFO:** `{d.get('country_name','N/A')} {d.get('country_flag','🌐')} - {d.get('brand','N/A')}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        + "\n".join(cards) +
        f"\n━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **GEN BY:** @{update.effective_user.username}"
    )
    await prog.delete()
    await update.message.reply_text(res, parse_mode="Markdown")

async def chk_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    match = re.search(r"(\d{15,16})\|(\d{2})\|(\d{2,4})\|(\d{3,4})", update.message.text)
    if not match: return

    prog = await show_progress(update.message, "Connecting to chkr.cc API...")
    data = await bot_engine.check_cc_api(match.group())
    
    if data:
        status = data.get('status', 'Die')
        icon = "APPROVED 🔥" if status == "Live" else "DECLINED ❌"
        card = data.get('card', {})
        res = (
            f"💠 **PIRATEs CHECKER 2026** ⚡\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"💳 **CC:** `{match.group()}`\n"
            f"📡 **STATUS:** `{icon}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"🏦 **BANK:** `{card.get('bank', 'N/A')}`\n"
            f"🌍 **COUNTRY:** `{card.get('country_name', 'N/A')}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **CHECKED BY:** @{update.effective_user.username}"
        )
        await prog.delete()
        await update.message.reply_text(res, parse_mode="Markdown")
    else:
        await prog.edit_text("❌ API Timeout!")

if __name__ == '__main__':
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("chk", chk_handler))
    app.add_handler(CommandHandler("gen", gen_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chk_handler))
    
    print("🤖 Bot is starting...")
    app.run_polling()
