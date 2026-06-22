import os
import aiohttp
import asyncio
from datetime import datetime
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

COINGECKO_BASE = "https://api.coingecko.com/api/v3"
BINANCE_BASE = "https://api.binance.com/api/v3"
FEAR_GREED_URL = "https://api.alternative.me/fng/?limit=1"

COIN_ID_MAP = {
    "BTC": "bitcoin", "ETH": "ethereum", "BNB": "binancecoin",
    "SOL": "solana", "XRP": "ripple", "ADA": "cardano",
    "AVAX": "avalanche-2", "DOT": "polkadot", "MATIC": "matic-network",
    "LINK": "chainlink", "UNI": "uniswap", "ATOM": "cosmos",
    "LTC": "litecoin", "DOGE": "dogecoin", "SHIB": "shiba-inu",
    "TON": "the-open-network", "TRX": "tron", "OP": "optimism",
    "ARB": "arbitrum", "SUI": "sui",
}

BINANCE_SYMBOL_MAP = {
    "BTC": "BTCUSDT", "ETH": "ETHUSDT", "BNB": "BNBUSDT",
    "SOL": "SOLUSDT", "XRP": "XRPUSDT", "ADA": "ADAUSDT",
    "AVAX": "AVAXUSDT", "DOT": "DOTUSDT", "MATIC": "MATICUSDT",
    "LINK": "LINKUSDT", "UNI": "UNIUSDT", "ATOM": "ATOMUSDT",
    "LTC": "LTCUSDT", "DOGE": "DOGEUSDT", "SHIB": "SHIBUSDT",
    "TON": "TONUSDT", "TRX": "TRXUSDT", "OP": "OPUSDT",
    "ARB": "ARBUSDT", "SUI": "SUIUSDT",
}


class CryptoAnalyzer:

    async def _fetch(self, url, params=None):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as r:
                    if r.status == 200:
                        return await r.json()
        except Exception as e:
            print(f"Fetch error {url}: {e}")
        return None

    def _get_coin_id(self, symbol):
        return COIN_ID_MAP.get(symbol, symbol.lower())

    def _get_binance_symbol(self, symbol):
        return BINANCE_SYMBOL_MAP.get(symbol, f"{symbol}USDT")

    async def get_price(self, symbol):
        coin_id = self._get_coin_id(symbol)
        data = await self._fetch(f"{COINGECKO_BASE}/simple/price", {
            "ids": coin_id,
            "vs_currencies": "usd",
            "include_24hr_change": "true",
            "include_24hr_vol": "true",
            "include_market_cap": "true"
        })
        if not data or coin_id not in data:
            return f"❌ Could not find price for {symbol}. Check the symbol."

        d = data[coin_id]
        price = d.get("usd", 0)
        change = d.get("usd_24h_change", 0)
        vol = d.get("usd_24h_vol", 0)
        mcap = d.get("usd_market_cap", 0)
        emoji = "🟢" if change >= 0 else "🔴"

        return (
            f"💰 *{symbol} Price*\n\n"
            f"Price: `${price:,.4f}`\n"
            f"{emoji} 24h Change: `{change:.2f}%`\n"
            f"📦 Volume 24h: `${vol:,.0f}`\n"
            f"🏦 Market Cap: `${mcap:,.0f}`\n\n"
            f"_Updated: {datetime.utcnow().strftime('%H:%M UTC')}_"
        )

    async def _get_market_data(self, symbol):
        coin_id = self._get_coin_id(symbol)
        cg_data, binance_klines = await asyncio.gather(
            self._fetch(f"{COINGECKO_BASE}/coins/{coin_id}", {
                "localization": "false",
                "tickers": "false",
                "community_data": "false",
                "developer_data": "false"
            }),
            self._fetch(f"{BINANCE_BASE}/klines", {
                "symbol": self._get_binance_symbol(symbol),
                "interval": "1d",
                "limit": 14
            })
        )
        return cg_data, binance_klines

    def _calc_rsi(self, klines, period=14):
        if not klines or len(klines) < period + 1:
            return None
        closes = [float(k[4]) for k in klines]
        gains, losses = [], []
        for i in range(1, len(closes)):
            diff = closes[i] - closes[i - 1]
            gains.append(max(diff, 0))
            losses.append(max(-diff, 0))
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        return round(100 - (100 / (1 + rs)), 2)

    def _calc_sma(self, klines, period):
        if not klines or len(klines) < period:
            return None
        closes = [float(k[4]) for k in klines[-period:]]
        return round(sum(closes) / period, 4)

    async def technical_analysis(self, symbol):
        _, klines = await self._get_market_data(symbol)
        price_data = await self._fetch(f"{COINGECKO_BASE}/simple/price", {
            "ids": self._get_coin_id(symbol),
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        })

        coin_id = self._get_coin_id(symbol)
        current_price = price_data[coin_id]["usd"] if price_data and coin_id in price_data else "N/A"
        change_24h = price_data[coin_id].get("usd_24h_change", 0) if price_data and coin_id in price_data else 0

        rsi = self._calc_rsi(klines) if klines else None
        sma7 = self._calc_sma(klines, 7) if klines else None
        sma14 = self._calc_sma(klines, 14) if klines else None

        rsi_signal = "⚖️ Neutral"
        if rsi:
            if rsi < 30:
                rsi_signal = "🟢 Oversold (potential buy)"
            elif rsi > 70:
                rsi_signal = "🔴 Overbought (potential sell)"

        sma_signal = "⚖️ Neutral"
        if sma7 and sma14:
            sma_signal = "🟢 Bullish (7 > 14 SMA)" if sma7 > sma14 else "🔴 Bearish (7 < 14 SMA)"

        return (
            f"📈 *Technical Analysis — {symbol}*\n\n"
            f"💵 Price: `${current_price:,.4f}` ({change_24h:.2f}% 24h)\n\n"
            f"*RSI (14):* `{rsi if rsi else 'N/A'}`\n"
            f"Signal: {rsi_signal}\n\n"
            f"*SMA 7:* `{sma7 if sma7 else 'N/A'}`\n"
            f"*SMA 14:* `{sma14 if sma14 else 'N/A'}`\n"
            f"Trend: {sma_signal}\n\n"
            f"_⚠️ Not financial advice. DYOR!_"
        )

    async def get_sentiment(self):
        data = await self._fetch(FEAR_GREED_URL)
        if not data:
            return "❌ Could not fetch sentiment data."

        fng = data["data"][0]
        value = int(fng["value"])
        classification = fng["value_classification"]
        timestamp = fng["timestamp"]
        dt = datetime.utcfromtimestamp(int(timestamp)).strftime("%Y-%m-%d")

        if value <= 25:
            emoji = "😱"
        elif value <= 45:
            emoji = "😟"
        elif value <= 55:
            emoji = "😐"
        elif value <= 75:
            emoji = "😊"
        else:
            emoji = "🤑"

        bar = "█" * (value // 10) + "░" * (10 - value // 10)

        prompt = (
            f"The crypto Fear & Greed Index is currently {value}/100 ({classification}). "
            f"In 2-3 sentences, explain what this means for traders right now and what to watch out for."
        )
        ai_comment = await self._ask_gemini(prompt)

        return (
            f"😱 *Crypto Fear & Greed Index*\n\n"
            f"{emoji} *{classification}*\n"
            f"`{bar}` {value}/100\n"
            f"📅 Date: {dt}\n\n"
            f"🤖 *AI Insight:*\n{ai_comment}\n\n"
            f"_Extreme Fear = possible buying opportunity_\n"
            f"_Extreme Greed = market may be overheated_"
        )

    async def _ask_gemini(self, prompt):
        try:
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"AI unavailable: {e}"

    async def full_analysis(self, symbol):
        coin_id = self._get_coin_id(symbol)
        cg_data, klines = await self._get_market_data(symbol)
        fear_data = await self._fetch(FEAR_GREED_URL)

        if not cg_data:
            return f"❌ Could not fetch data for {symbol}. Check the symbol name."

        market = cg_data.get("market_data", {})
        price = market.get("current_price", {}).get("usd", "N/A")
        change_1h = market.get("price_change_percentage_1h_in_currency", {}).get("usd", 0)
        change_24h = market.get("price_change_percentage_24h", 0)
        change_7d = market.get("price_change_percentage_7d", 0)
        high_24h = market.get("high_24h", {}).get("usd", "N/A")
        low_24h = market.get("low_24h", {}).get("usd", "N/A")
        vol = market.get("total_volume", {}).get("usd", 0)
        mcap = market.get("market_cap", {}).get("usd", 0)
        ath = market.get("ath", {}).get("usd", "N/A")
        ath_change = market.get("ath_change_percentage", {}).get("usd", 0)

        rsi = self._calc_rsi(klines) if klines else "N/A"
        sma7 = self._calc_sma(klines, 7) if klines else "N/A"
        sma14 = self._calc_sma(klines, 14) if klines else "N/A"

        fng_value = fear_data["data"][0]["value"] if fear_data else "N/A"
        fng_class = fear_data["data"][0]["value_classification"] if fear_data else "N/A"

        description = cg_data.get("description", {}).get("en", "")[:300]

        prompt = f"""
You are an expert crypto market analyst. Analyze this data for {symbol} and give a clear trader-focused summary.

MARKET DATA:
- Current Price: ${price}
- 1h Change: {change_1h:.2f}%
- 24h Change: {change_24h:.2f}%
- 7d Change: {change_7d:.2f}%
- 24h High: ${high_24h} | Low: ${low_24h}
- Volume 24h: ${vol:,.0f}
- Market Cap: ${mcap:,.0f}
- ATH: ${ath} ({ath_change:.1f}% from ATH)

TECHNICAL INDICATORS:
- RSI (14): {rsi}
- SMA 7: {sma7}
- SMA 14: {sma14}

MARKET SENTIMENT:
- Fear & Greed Index: {fng_value}/100 ({fng_class})

Give a structured analysis with:
1. 📊 Trend (1-2 sentences)
2. 🎯 Key levels to watch (support/resistance based on data)
3. ⚠️ Main risks right now
4. 💡 Overall outlook (bullish/bearish/neutral and why)
Keep it concise and actionable for a trader. No fluff.
"""
        ai_analysis = await self._ask_gemini(prompt)

        return (
            f"🔍 *Full Analysis — {symbol}*\n\n"
            f"💵 Price: `${price:,.4f}`\n"
            f"1h: `{change_1h:.2f}%` | 24h: `{change_24h:.2f}%` | 7d: `{change_7d:.2f}%`\n"
            f"📊 High: `${high_24h:,.2f}` | Low: `${low_24h:,.2f}`\n"
            f"📦 Vol: `${vol:,.0f}` | MCap: `${mcap:,.0f}`\n\n"
            f"📈 RSI: `{rsi}` | SMA7: `{sma7}` | SMA14: `{sma14}`\n"
            f"😱 Fear & Greed: `{fng_value}/100` ({fng_class})\n\n"
            f"🤖 *AI Analysis:*\n{ai_analysis}\n\n"
            f"_⚠️ Not financial advice. Always DYOR!_"
        )

    async def get_signal(self, symbol):
        coin_id = self._get_coin_id(symbol)
        price_data, klines, fear_data = await asyncio.gather(
            self._fetch(f"{COINGECKO_BASE}/simple/price", {
                "ids": coin_id,
                "vs_currencies": "usd",
                "include_24hr_change": "true",
                "include_24hr_vol": "true"
            }),
            self._fetch(f"{BINANCE_BASE}/klines", {
                "symbol": self._get_binance_symbol(symbol),
                "interval": "4h",
                "limit": 30
            }),
            self._fetch(FEAR_GREED_URL)
        )

        if not price_data or coin_id not in price_data:
            return f"❌ Could not fetch data for {symbol}."

        price = price_data[coin_id]["usd"]
        change_24h = price_data[coin_id].get("usd_24h_change", 0)
        vol = price_data[coin_id].get("usd_24h_vol", 0)
        rsi = self._calc_rsi(klines, 14) if klines else "N/A"
        sma7 = self._calc_sma(klines, 7) if klines else "N/A"
        sma14 = self._calc_sma(klines, 14) if klines else "N/A"
        fng = fear_data["data"][0]["value"] if fear_data else "N/A"
        fng_class = fear_data["data"][0]["value_classification"] if fear_data else "N/A"

        prompt = f"""
You are a professional crypto trader. Based on the data below for {symbol}, give a clear BUY / SELL / HOLD / WAIT signal.

DATA:
- Price: ${price}
- 24h Change: {change_24h:.2f}%
- Volume 24h: ${vol:,.0f}
- RSI (14, 4h): {rsi}
- SMA 7 (4h): {sma7}
- SMA 14 (4h): {sma14}
- Fear & Greed: {fng}/100 ({fng_class})

Respond with exactly this format:
SIGNAL: [BUY/SELL/HOLD/WAIT]
CONFIDENCE: [Low/Medium/High]
ENTRY ZONE: $[price range]
STOP LOSS: $[price]
TARGET 1: $[price]
TARGET 2: $[price]
REASON: [2-3 sentences max explaining the signal]
RISK: [1 main risk to this trade]
"""
        signal = await self._ask_gemini(prompt)

        return (
            f"🎯 *Trading Signal — {symbol}*\n\n"
            f"💵 Current Price: `${price:,.4f}`\n"
            f"📊 RSI: `{rsi}` | F&G: `{fng}/100`\n\n"
            f"```\n{signal}\n```\n\n"
            f"_⚠️ AI-generated signal. Not financial advice. Use proper risk management!_"
        )

    async def get_top_coins(self):
        data = await self._fetch(f"{COINGECKO_BASE}/coins/markets", {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 10,
            "page": 1,
            "sparkline": "false",
            "price_change_percentage": "24h"
        })
        if not data:
            return "❌ Could not fetch top coins."

        lines = ["🔝 *Top 10 Coins by Market Cap*\n"]
        for i, coin in enumerate(data, 1):
            change = coin.get("price_change_percentage_24h", 0) or 0
            emoji = "🟢" if change >= 0 else "🔴"
            lines.append(
                f"{i}. *{coin['symbol'].upper()}* — `${coin['current_price']:,.4f}` "
                f"{emoji} `{change:.2f}%`"
            )

        lines.append(f"\n_Updated: {datetime.utcnow().strftime('%H:%M UTC')}_")
        return "\n".join(lines)
