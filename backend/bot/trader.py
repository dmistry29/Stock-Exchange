import asyncio
from backend.core.orderbook import OrderBook
from backend.core.matching import match_order
from backend.infra.database import TradeDatabase
from backend.bot.strategy import TradingStrategy

class TradingBot:
    def __init__(self, book: OrderBook, db: TradeDatabase):
        self.book = book
        self.db = db
        self.strategy = TradingStrategy()
        self.running = False

    async def run(self):
        """
        The Infinite Loop:
        1. Get Signal -> 2. Execute Match -> 3. Save to DB
        """
        print("Trading Bot: Online. Hunting for trades...")
        self.running = True
        
        while self.running:
            # 1. Ask the Strategy for a decision
            order = self.strategy.get_order(self.book)
            
            if order:
                # 2. Execute against the Engine
                # We do NOT just add it to the book. We try to MATCH it.
                trades = match_order(self.book, order)
                
                # 3. Handle Results
                if trades:
                    print(f"BOT EXECUTION: {len(trades)} trade(s) generated!")
                    for trade in trades:
                        # Save to SQLite asynchronously
                        await self.db.add_trade(trade)
                else:
                    # If no match, the order rests in the book (providing liquidity)
                    pass
            
            # Trade every 2 seconds to keep the demo readable
            await asyncio.sleep(2)