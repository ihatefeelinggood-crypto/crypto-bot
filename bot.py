async def get_signal(self, coin: str):
    # ... your existing data fetching ...
    
    return f"""
📊 **{coin} SIGNAL** (AI + Technical)

🟢 **Bias**: Strongly Bullish
📍 Current Price: ${current_price:,}

**Entry Zone**: ${entry_low} - ${entry_high}
**Take Profit Targets**:
   • TP1: ${tp1} (+{profit1}%)
   • TP2: ${tp2} (+{profit2}%)

🛑 Stop Loss: ${stop_loss} (-{risk}%)

**Reason**: {reason} (BTC dominance dropping + high volume inflow into {coin} altcoins)
    """
