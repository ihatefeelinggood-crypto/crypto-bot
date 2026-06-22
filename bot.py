import logging
import os
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes

from analyzer import CryptoAnalyzer

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable is missing")

analyzer = CryptoAnalyzer()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 Welcome to CryptoAI Bot!\n\n"
        "Commands:\n"
        "/analyze BTC\n"
        "/signal ETH\n"
        "/sentiment\n"
        "/ta SOL\n"
        "/price BNB\n"
        "/top"
    )
    await update.message.reply_text(welcome_text)


async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /signal BTC")
        return

    await update.message.reply_text("🔄 Generating signal...")
    try:
        result = await analyzer.get_signal(context.args[0].upper())
        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text(f"❌ Error generating signal: {str(e)}")


async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /analyze BTC")
        return

    await update.message.reply_text("🔍 Analyzing market...")
    try:
        result = await analyzer.full_analysis(context.args[0].upper())
        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text(f"❌ Error in analysis: {str(e)}")


async def sentiment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Checking market sentiment...")
    try:
        result = await analyzer.get_sentiment()
        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text(f"❌ Error getting sentiment: {str(e)}")


async def ta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /ta BTC")
        return

    await update.message.reply_text("📉 Running technical analysis...")
    try:
        result = await analyzer.technical_analysis(context.args[0].upper())
        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text(f"❌ Error in TA: {str(e)}")


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /price BTC")
        return

    try:
        result = await analyzer.get_price(context.args[0].upper())
        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text(f"❌ Error getting price: {str(e)}")


async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏆 Fetching top coins...")
    try:
        result = await analyzer.get_top_coins()
        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text(f"❌ Error getting top coins: {str(e)}")


async def set_commands(application: Application):
    commands = [
        BotCommand("start", "Start bot"),
        BotCommand("analyze", "AI market analysis"),
        BotCommand("signal", "Trading signal"),
        BotCommand("sentiment", "Fear & Greed"),
        BotCommand("ta", "Technical analysis"),
        BotCommand("price", "Price check"),
        BotCommand("top", "Top 10 coins"),
    ]
    await application.bot.set_my_commands(commands)


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).post_init(set_commands).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("analyze", analyze))
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CommandHandler("sentiment", sentiment))
    app.add_handler(CommandHandler("ta", ta))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("top", top))

    print("🤖 Bot is running... Polling started")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
