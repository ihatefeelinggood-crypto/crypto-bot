import logging
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes

from analyzer import CryptoAnalyzer

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_TOKEN = "YOUR_TOKEN_HERE"

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

    await update.message.reply_text("Generating signal...")
    result = await analyzer.get_signal(context.args[0].upper())
    await update.message.reply_text(result)


async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /analyze BTC")
        return

    await update.message.reply_text("Analyzing...")
    result = await analyzer.full_analysis(context.args[0].upper())
    await update.message.reply_text(result)


async def sentiment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Checking sentiment...")
    result = await analyzer.get_sentiment()
    await update.message.reply_text(result)


async def ta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /ta BTC")
        return

    await update.message.reply_text("Running technical analysis...")
    result = await analyzer.technical_analysis(context.args[0].upper())
    await update.message.reply_text(result)


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /price BTC")
        return

    result = await analyzer.get_price(context.args[0].upper())
    await update.message.reply_text(result)


async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = await analyzer.get_top_coins()
    await update.message.reply_text(result)


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

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
