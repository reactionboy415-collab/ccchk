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

# --- RENDER PORT FIX ---
web_app = Flask(__name__)
@web_app.route('/')
def health_check():
    return "Pirate Bot is Alive!", 200

def run_flask():
    # Render provides a PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)

# --- CONFIG ---
BOT_TOKEN = "8318488317:AAGGuMfRMqOaGv0ZJfyAedAFRULVHVvy8qI"
ADMIN_HANDLE = "@dev2dex"

logging.basicConfig(level=logging.INFO)

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
    p = await pirate_db_progress(update.message, "Please wait, registering your account on DB...")
    banner = f"https://placehold.jp/80/000000/ffd700/1200x600.png?text=WELCOME%20{urllib.parse.quote(update.effective_user.first_name.upper())}"
    welcome = f"🎊 **WELCOME!** 🎊\n━━━━━━━━━━━━━━\n🚀 **PIRATEs CHECKER v5.0**\nGateway: `chkr.cc Premium` 🔒\n━━━━━━━━━━━━━━\n🔹 `/chk` - Check CC\n🔹 `/gen` - Generate Cards\n━━━━━━━━━━━━━━\n🛠 **Dev:** {ADMIN_HANDLE}"
    await p.delete()
    await update.message.reply_photo(photo=banner, caption=welcome, parse_mode="Markdown")

async def gen_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bin_m = re.search(r'\d{6}', update.message.text)
    if not bin_m: return
    p = await pirate_db_progress(update.message, "Fetching BIN data & syncing with database...")
    bin_num = bin_m.group()
    cards = [f"`{bin_num}{random.randint(1000000000,9999999999)}|{random.choice(['01','12'])}|{random.randint(2026,2030)}|{random.randint(100,999)}`" for _ in range(10)]
    res = f"💠 **PIRATEs GENERATOR** ⚡\n━━━━━━━━━━━━━━\n🏦 **BIN:** `{bin_num}`\n━━━━━━━━━━━━━━\n" + "\n".join(cards) + f"\n━━━━━━━━━━━━━━\n👤 **GEN BY:** @{update.effective_user.username}"
    await p.delete()
    await update.message.reply_text(res, parse_mode="Markdown")

async def chk_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m = re.search(r"(\d{15,16})\|(\d{2})\|(\d{2,4})\|(\d{3,4})", update.message.text)
    if not m: return
    p = await pirate_db_progress(update.message, "Verifying identity & connecting to Gateway...")
    # Fake API response for logic demonstration
    await asyncio.sleep(1)
    await p.edit_text("✅ **Success!** Card details sent to Pirate Engine.")
    # Here you would add your chkr.cc logic from before

if __name__ == '__main__':
    # Start Flask in a background thread
    Thread(target=run_flask).start()
    
    # Start Bot
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("chk", chk_handler))
    app.add_handler(CommandHandler("gen", gen_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chk_handler))
    
    print("🏴‍☠️ Pirate Bot is Online with Port Fix!")
    app.run_polling(drop_pending_updates=True)
