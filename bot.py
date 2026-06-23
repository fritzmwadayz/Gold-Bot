from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import BOT_TOKEN, CHAT_ID, INTERVAL_MINUTES
from analyzer import run_analysis


def format_message(s: dict) -> str:
    emoji = "🟢" if s["signal"] == "BUY" else "🔴"
    tp = s["trade_plan"]

    return (
        f"{emoji} GOLD SIGNAL - {s['signal']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Price: ${s['price']}\n"
        f"📊 RSI: {s['indicators']['rsi']} | Structure: {s['structure']}\n"
        f"📈 EMA50: ${s['indicators']['ema50']} | EMA200: ${s['indicators']['ema200']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 Confidence: {s['confidence']}%\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 ENTRY: ${tp['entry']}\n"
        f"🛑 STOP LOSS: ${tp['sl']}\n"
        f"✅ TAKE PROFIT: ${tp['tp']}\n"
        f"📊 R:R: {tp['rr']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⏰ {s['timestamp']}"
    )

CHAT_ID_STORAGE = None  # temp, just for testing

async def send_signal(context: ContextTypes.DEFAULT_TYPE):
    signal = run_analysis()
    if signal:
        await context.bot.send_message(chat_id=CHAT_ID_STORAGE, text=format_message(signal))
        print(f"[bot] Sent {signal['signal']} signal")
    else:
        print("[bot] No signal this cycle")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CHAT_ID_STORAGE
    CHAT_ID_STORAGE = update.effective_chat.id
    print(f"[bot] Captured chat ID: {CHAT_ID_STORAGE}")
    await update.message.reply_text("🤖 Bot active. Chat ID captured. Signals will start automatically.")

async def signal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Checking...")
    signal = run_analysis()
    if signal:
        await update.message.reply_text(format_message(signal))
    else:
        await update.message.reply_text("❌ No signal right now. Waiting...")


def main():
    if not BOT_TOKEN:
        print("[bot] Error: BOT_TOKEN required in .env")
        return

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal_cmd))

    job_queue = app.job_queue
    job_queue.run_repeating(send_signal, interval=INTERVAL_MINUTES * 60, first=10)

    print(f"[bot] Started. Checking every {INTERVAL_MINUTES} min. Send /start to capture chat ID.")
    app.run_polling()

if __name__ == "__main__":
    main()