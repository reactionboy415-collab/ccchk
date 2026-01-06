import logging
import re
import asyncio
import requests
import random
import urllib.parse
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIG ---
BOT_TOKEN = "8318488317:AAGGuMfRMqOaGv0ZJfyAedAFRULVHVvy8qI"
ADMIN_ID = 7840042951
ADMIN_HANDLE = "@dev2dex"

logging.basicConfig(level=logging.INFO)

# --- PROGRESS BAR HELPER ---
async def pirate_progress(message, status_text):
    """Real-time progress bar for that professional feel"""
    bars = [
        "🌑 [..........] 0%", 
        "🌒 [██........] 20%", 
        "🌓 [████......] 45%", 
        "🌔 [███████...] 75%", 
        "🌕 [██████████] 100%"
    ]
    prog_msg = await message.reply_text(f"⚔️ **Pirate System**\n`{bars[0]}`\n🛰 _{status_text}_", parse_mode="Markdown")
    for bar in bars[1:]:
        await asyncio.sleep(0.5)
        await prog_msg.edit_text(f"⚔️ **Pirate System**\n`{bar}`\n🛰 _{status_text}_", parse_mode="Markdown")
    return prog_msg

# --- CORE FUNCTIONS ---
def get_bin_info(bin_num):
    try:
        r = requests.get(f"https://bins.antipublic.cc/bins/{bin_num[:6]}", timeout=5).json()
        return r
    except: return {}

async def chk_api(cc):
    try:
        url = "https://api.chkr.cc/"
        payload = {"data": cc, "charge": False}
        r = requests.post(url, json=payload, timeout=20).json()
        return r
    except: return None

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # Custom Progress for DB Registration
    p = await pirate_progress(update.message, "Please wait, registering your account on DB...")
    
    banner = f"https://placehold.jp/80/000000/ffd700/1200x600.png?text=WELCOME%20{urllib.parse.quote(user.first_name.upper())}"
    welcome = (
        f"🎊 **WELCOME, {user.first_name.upper()}!** 🎊\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🚀 **PIRATEs CHECKER v5.0**\n"
        "Gateway: `chkr.cc Premium` 🔒\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🔹 `/chk CARD|MM|YY|CVV` - Check CC\n"
        "🔹 `/gen BIN` - Generate Cards\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"🛠 **Dev:** {ADMIN_HANDLE}"
    )
    await p.delete()
    await update.message.reply_photo(photo=banner, caption=welcome, parse_mode="Markdown")

async def gen_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bin_m = re.search(r'\d{6}', update.message.text)
    if not bin_m: return
    
    p = await pirate_progress(update.message, "Analyzing BIN & Generating secure cards...")
    bin_num = bin_m.group()
    d = get_bin_info(bin_num)
    
    cards = []
    for _ in range(10):
        # Basic generation with common years
        c = f"{bin_num}{random.randint(1000000000, 9999999999)}|{random.choice(['01','12'])}|{random.randint(2026,2030)}|{random.randint(100,999)}"
        cards.append(f"`{c}`")

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
    await p.delete()
    await update.message.reply_text(res, parse_mode="Markdown")

async def chk_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m = re.search(r"(\d{15,16})\|(\d{2})\|(\d{2,4})\|(\d{3,4})", update.message.text)
    if not m: return

    p = await pirate_progress(update.message, "Handshaking with API Gateway...")
    data = await chk_api(m.group())
    
    if data:
        st = data.get('status', 'Die')
        icon = "APPROVED 🔥" if st == "Live" else "DECLINED ❌"
        card = data.get('card', {})
        res = (
            f"💠 **PIRATEs CHECKER 2026** ⚡\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"💳 **CC:** `{m.group()}`\n"
            f"📡 **STATUS:** `{icon}`\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"🏦 **BANK:** `{card.get('bank', 'N/A')}`\n"
            f"🌍 **COUNTRY:** `{card.get('country_name', 'N/A')}`\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **CHECKED BY:** @{update.effective_user.username}"
        )
        await p.delete()
        await update.message.reply_text(res, parse_mode="Markdown")
    else:
        await p.edit_text("❌ **API CONNECTION FAILED!**")

if __name__ == '__main__':
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("chk", chk_handler))
    application.add_handler(CommandHandler("gen", gen_handler))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chk_handler))
    
    application.run_polling()
    
