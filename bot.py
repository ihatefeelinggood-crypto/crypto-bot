import logging
import aiohttp
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = "YOUR_TOKEN_HERE"   # ← CHANGE THIS

# ====================== COMMAND HANDLERS ======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 Welcome to CryptoAI Bot!\n\n"
        "Powered by Gemini AI + Live Market Data\n\n"
        "Commands:\n"
        "📊 /analyze BTC — Full AI market analysis\n"
        "📈 /signal ETH — Entry/exit signal\n"
        "😨 /sentiment — Market fear & greed\n"
        "📉 /ta SOL — Technical indicators\n"
        "💰 /price BNB — Quick price check\n"
        "🏆 /top — Top 10 coins by market cap\n\n"
        "Not financial advice. Always DYOR!"
    )
    await update.message.reply_text(welcome_text)

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /signal ETH")
        return
    coin = context.args[0].upper()
    await update.message.reply_text(f"📈 Generating signal for {coin}...\n(Replace this with real logic)")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /analyze BTC")
        return
    coin = context.args[0].upper()
    await update.message.reply_text(f"🔍 AI Analysis for {coin}...\n(Replace this with Gemini API call)")

async def sentiment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("😨 Current Market Sentiment: Fear & Greed Index\n(Replace with real data)")

async def ta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /ta SOL")
        return
    coin = context.args[0].upper()
    await update.message.reply_text(f"📉 Technical Analysis for {coin}...\n(Replace with real TA)")

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /price BNB")
        return
    coin = context.args[0].upper()
    await update.message.reply_text(f"💰 Current price of {coin}...\n(Replace with real price API)")

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏆 Top 10 Coins by Market Cap...\n(Replace with real data)")

# ====================== MAIN ======================

async def set_commands(application: Application):
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("analyze", "Full AI market analysis"),
        BotCommand("signal", "Entry/exit signal"),
        BotCommand("sentiment", "Market fear & greed"),
        BotCommand("ta", "Technical indicators"),
        BotCommand("price", "Quick price check"),
        BotCommand("top", "Top 10 coins"),
    ]
    await application.bot.set_my_commands(commands)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).post_init(set_commands).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CommandHandler("analyze", analyze))
    app.add_handler(CommandHandler("sentiment", sentiment))
    app.add_handler(CommandHandler("ta", ta))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("top", top))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
