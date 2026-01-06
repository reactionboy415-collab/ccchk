import logging
import re
import asyncio
import requests
import random
import urllib.parse
import os
from threading import Thread
from flask import Flask
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- RENDER ALIVE FIX ---
web_app = Flask(__name__)
@web_app.route('/')
def health_check(): return "Pirate Bot Alive", 200
def run_flask():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)

# --- CONFIG ---
BOT_TOKEN = "8318488317:AAGGuMfRMqOaGv0ZJfyAedAFRULVHVvy8qI"
ADMIN_HANDLE = "@dev2dex"

logging.basicConfig(level=logging.INFO)

class PirateBotEngine:
    def __init__(self):
        self.session = requests.Session()
        self.ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    def get_bin_info(self, bin_num):
        try:
            r = requests.get(f"https://bins.antipublic.cc/bins/{bin_num[:6]}", timeout=5).json()
            return r
        except: return {}

    async def check_cc_api(self, cc_details):
        # Your exact script logic for chkr.cc
        url = "https://api.chkr.cc/"
        payload = {"data": cc_details, "charge": False}
        headers = {"User-Agent": self.ua, "Content-Type": "application/json"}
        try:
            # Step 1: Analytics bypass
            trk_url = "https://trk.caseads.com/api/send"
            trk_payload = {"type": "event", "payload": {"website": "919a2102-c2ec-411c-b432-67d0ac721446", "name": "start-check"}}
            self.session.post(trk_url, json=trk_payload, timeout=5)
            await asyncio.sleep(1)
            # Step 2: Main Check
            response = self.session.post(url, json=payload, headers=headers, timeout=25)
            return response.json()
        except: return None

bot_engine = PirateBotEngine()

# --- PROGRESS BAR ---
async def pirate_db_progress(message, action_text):
    stages = ["🌑 [..........] 0%", "🌒 [██........] 25%", "🌓 [█████.....] 50%", "🌔 [███████...] 80%", "🌕 [██████████] 100%"]
    prog_msg = await message.reply_text(f"⏳ **Processing...**\n`{stages[0]}`\n📡 _{action_text}_", parse_mode="Markdown")
    for stage in stages[1:]:
        await asyncio.sleep(0.4)
        try: await prog_msg.edit_text(f"⏳ **Processing...**\n`{stage}`\n📡 _{action_text}_", parse_mode="Markdown")
        except: pass
    return prog_msg

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    p = await pirate_db_progress(update.message, "Please wait, registering your account on DB...")
    
    banner = f"https://placehold.jp/80/000000/ffd700/1200x600.png?text=WELCOME%20{urllib.parse.quote(user.first_name.upper())}"
    welcome = (
        f"🎊 WELCOME! {user.first_name}🎊\n"
        "━━━━━━━━━━━━━━\n"
        "🚀 **PIRATEs CHECKER v1.0**\n"
        "Gateway: `Stripe Premium 🔒` \n"
        "━━━━━━━━━━━━━━\n"
        "🔹 /chk - Check CC\n"
        "🔹 /gen - Generate Cards\n"
        "━━━━━━━━━━━━━━\n"
        f"🛠 Dev: {ADMIN_HANDLE}"
    )
    await p.delete()
    await update.message.reply_photo(photo=banner, caption=welcome, parse_mode="Markdown")

async def gen_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bin_m = re.search(r'\d{6}', update.message.text)
    if not bin_m: return
    p = await pirate_db_progress(update.message, "Fetching BIN data & syncing with database...")
    
    bin_num = bin_m.group()
    d = bot_engine.get_bin_info(bin_num)
    cards = [f"{bin_num}{random.randint(1000000000,9999999999)}|{random.choice(['01','12'])}|{random.randint(2026,2030)}|{random.randint(100,999)}" for _ in range(10)]
    
    res = (
        f"💠 **PIRATEs GENERATOR** ⚡\n"
        "━━━━━━━━━━━━━━\n"
        f"🏦 **BIN:** `{bin_num}`\n"
        f"🌍 **INFO:** `{d.get('country_name','N/A')} {d.get('country_flag','🌐')} - {d.get('brand','N/A')}`\n"
        f"🏛 **BANK:** `{d.get('bank','N/A')}`\n"
        "━━━━━━━━━━━━━━\n" + 
        "\n".join([f"`{c}`" for c in cards]) + 
        f"\n━━━━━━━━━━━━━━\n👤 **GEN BY:** @{update.effective_user.username}"
    )
    await p.delete()
    await update.message.reply_text(res, parse_mode="Markdown")

async def chk_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m = re.search(r"(\d{15,16})\|(\d{2})\|(\d{2,4})\|(\d{3,4})", update.message.text)
    if not m: return
    
    p = await pirate_db_progress(update.message, "Verifying identity & connecting to Gateway...")
    data = await bot_engine.check_cc_api(m.group())
    
    if data:
        status = data.get('status', 'Die')
        icon = "APPROVED 🔥" if status == "Live" else "DECLINED ❌"
        card = data.get('card', {})
        res = (
            f"💠 **PIRATEs CHECKER 2026** ⚡\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"💳 **CC:** `{m.group()}`\n"
            f"📡 **STATUS:** `{icon}`\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"🏦 **BANK:** `{card.get('bank', 'N/A')}`\n"
            f"🌍 **COUNTRY:** `{card.get('country_name', 'N/A')}`\n"
            f"🛠 **INFO:** `{card.get('brand','N/A')} - {card.get('type','N/A')}`\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **CHECKED BY:** @{update.effective_user.username}"
        )
        await p.delete()
        await update.message.reply_text(res, parse_mode="Markdown")
    else:
        await p.edit_text("❌ **API Timeout / Proxy Error**")

if __name__ == '__main__':
    Thread(target=run_flask).start()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("chk", chk_handler))
    app.add_handler(CommandHandler("gen", gen_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chk_handler))
    app.run_polling(drop_pending_updates=True)
