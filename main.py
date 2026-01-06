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
ADMIN_HANDLE = "@dev2dex"

logging.basicConfig(level=logging.INFO)

# --- PROGRESS BAR LOGIC ---
async def pirate_db_progress(message, action_text):
    """Shows a professional progress bar with DB registration text"""
    stages = [
        "🌑 [..........] 0%", 
        "🌒 [██........] 22%", 
        "🌓 [█████.....] 48%", 
        "🌔 [███████...] 76%", 
        "🌕 [██████████] 100%"
    ]
    # Creating the initial message
    prog_msg = await message.reply_text(
        f"⏳ **Processing...**\n`{stages[0]}`\n📡 _{action_text}_", 
        parse_mode="Markdown"
    )
    # Fast animation for better UX
    for stage in stages[1:]:
        await asyncio.sleep(0.4)
        await prog_msg.edit_text(
            f"⏳ **Processing...**\n`{stage}`\n📡 _{action_text}_", 
            parse_mode="Markdown"
        )
    return prog_msg

# --- API TOOLS ---
def get_bin_info(bin_num):
    try:
        r = requests.get(f"https://bins.antipublic.cc/bins/{bin_num[:6]}", timeout=5).json()
        return r
    except: return {}

async def call_chkr_api(cc):
    # Mimicking your script's logic
    try:
        url = "https://api.chkr.cc/"
        payload = {"data": cc, "charge": False}
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.post(url, json=payload, headers=headers, timeout=20).json()
        return r
    except: return None

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # Show progress bar on start
    p = await pirate_db_progress(update.message, "Please wait, registering your account on DB...")
    
    banner = f"https://placehold.jp/80/000000/ffd700/1200x600.png?text=WELCOME%20{urllib.parse.quote(user.first_name.upper())}"
    welcome_text = (
        f"🎊 **WELCOME, {user.first_name.upper()}!** 🎊\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🚀 **PIRATEs CHECKER v5.0**\n"
        "Gateway: `chkr.cc Premium` 🔒\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📜 **Commands:**\n"
        "🔹 `/chk CARD|MM|YY|CVV` - Check CC\n"
        "🔹 `/gen BIN` - Generate Cards\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"🛠 **Dev:** {ADMIN_HANDLE}"
    )
    await p.delete()
    await update.message.reply_photo(photo=banner, caption=welcome_text, parse_mode="Markdown")

async def gen_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bin_m = re.search(r'\d{6}', update.message.text)
    if not bin_m: return
    
    p = await pirate_db_progress(update.message, "Fetching BIN data & syncing with database...")
    bin_num = bin_m.group()
    d = get_bin_info(bin_num)
    
    # Generate 10 cards
    cards = []
    for _ in range(10):
        full_cc = f"{bin_num}{random.randint(1000000000, 9999999999)}"
        # Simple Luhn-like format for aesthetics
        card_str = f"`{full_cc}|{random.choice(['01','12'])}|{random.randint(2026,2030)}|{random.randint(100,999)}`"
        cards.append(card_str)

    res = (
        f"💠 **PIRATEs GENERATOR** ⚡\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏦 **BIN:** `{bin_num}`\n"
        f"🌍 **INFO:** `{d.get('country_name','N/A')} {d.get('country_flag','🌐')} - {d.get('brand','N/A')}`\n"
        f"🏛 **BANK:** `{d.get('bank','N/A')}`\n"
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

    p = await pirate_db_progress(update.message, "Verifying identity & connecting to Gateway...")
    data = await call_chkr_api(m.group())
    
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
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **CHECKED BY:** @{update.effective_user.username}"
        )
        await p.delete()
        await update.message.reply_text(res, parse_mode="Markdown")
    else:
        await p.edit_text("❌ **API Gateway Timeout!**")

async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "Main Menu"),
        BotCommand("chk", "Check Card"),
        BotCommand("gen", "Generate CC")
    ])

if __name__ == '__main__':
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("chk", chk_handler))
    app.add_handler(CommandHandler("gen", gen_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chk_handler))
    
    print("🏴‍☠️ Pirate Bot is Online!")
    app.run_polling(drop_pending_updates=True)
