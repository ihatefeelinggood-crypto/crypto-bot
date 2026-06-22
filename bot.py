import os
import logging
import asyncio
import aiohttp
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
from analyzer import CryptoAnalyzer

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
analyzer = CryptoAnalyzer()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "👋 *Welcome to CryptoAI Bot!*\n\n"
        "Powered by Gemini AI + Live Market Data\n\n"
        "*Commands:*\n"
        "📊 /analyze `BTC` — Full AI market analysis\n"
        "🎯 /signal `ETH` — Entry/exit signal\n"
        "😱 /sentiment — Market fear & greed\n"
        "📈 /ta `SOL` — Technical indicators\n"
        "💰 /price `BNB` — Quick price check\n"
        "🔝 /top — Top 10 coins by market cap\n\n"
        "_Not financial advice. Always DYOR!_"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")


async def price_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /price BTC")
        return
    coin = context.args[0].upper()
    await update.message.reply_text(f"⏳ Fetching price for {coin}...")
    result = await analyzer.get_price(coin)
    await update.message.reply_text(result, parse_mode="Markdown")


async def analyze_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /analyze BTC")
        return
    coin = context.args[0].upper()
    await update.message.reply_text(f"🔍 Analyzing {coin} with AI... Please wait 10-20 seconds.")
    result = await analyzer.full_analysis(coin)
    await update.message.reply_text(result, parse_mode="Markdown")


async def signal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /signal ETH")
        return
    coin = context.args[0].upper()
    await update.message.reply_text(f"🎯 Generating signal for {coin}...")
    result = await analyzer.get_signal(coin)
    await update.message.reply_text(result, parse_mode="Markdown")


async def sentiment_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("😱 Fetching market sentiment...")
    result = await analyzer.get_sentiment()
    await update.message.reply_text(result, parse_mode="Markdown")


async def ta_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /ta SOL")
        return
    coin = context.args[0].upper()
    await update.message.reply_text(f"📈 Running technical analysis for {coin}...")
    result = await analyzer.technical_analysis(coin)
    await update.message.reply_text(result, parse_mode="Markdown")


async def top_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔝 Fetching top 10 coins...")
    result = await analyzer.get_top_coins()
    await update.message.reply_text(result, parse_mode="Markdown")


async def set_commands(app):
    commands = [
        BotCommand("start", "Welcome message"),
        BotCommand("price", "Quick price check e.g. /price BTC"),
        BotCommand("analyze", "Full AI analysis e.g. /analyze ETH"),
        BotCommand("signal", "Entry/exit signal e.g. /signal SOL"),
        BotCommand("sentiment", "Market fear & greed index"),
        BotCommand("ta", "Technical indicators e.g. /ta BNB"),
        BotCommand("top", "Top 10 coins by market cap"),
    ]
    await app.bot.set_my_commands(commands)


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).post_init(set_commands).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price_cmd))
    app.add_handler(CommandHandler("analyze", analyze_cmd))
    app.add_handler(CommandHandler("signal", signal_cmd))
    app.add_handler(CommandHandler("sentiment", sentiment_cmd))
    app.add_handler(CommandHandler("ta", ta_cmd))
    app.add_handler(CommandHandler("top", top_cmd))

    logger.info("Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
