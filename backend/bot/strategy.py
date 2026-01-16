import random
from typing import Optional
from backend.core.datatypes import Order, Side, OrderType
from backend.core.orderbook import OrderBook

class TradingStrategy:
    def get_order(self, book: OrderBook) -> Optional[Order]:
        """
        Analyzes the book and returns a new Order to execute.
        Returns None if the book is empty or we shouldn't trade.
        """
        best_bid = book.get_best_bid()
        best_ask = book.get_best_ask()

        # 1. Safety Check: We can't trade if the book is empty
        if not best_bid or not best_ask:
            return None

        # 2. Calculate Mid-Price (Fair Value)
        mid_price = (best_bid.price + best_ask.price) / 2

        # 3. Decision Logic (Randomized for Demo Purposes)
        # In a real interview, you'd calculate Moving Averages here.
        # We start with a 50/50 chance to Buy or Sell.
        side = Side.BUY if random.random() < 0.5 else Side.SELL
        
        # 4. Aggressive Pricing (To ensure a MATCH happens)
        # If we want to Buy, we bid slightly ABOVE the best ask (Crossing the spread)
        # If we want to Sell, we ask slightly BELOW the best bid
        price_offset = 10.0 # $10 aggressive offset
        
        if side == Side.BUY:
            price = best_ask.price + price_offset
        else:
            price = best_bid.price - price_offset

        # 5. Create the Order
        qty = 0.01 + (random.random() * 0.05) # Random quantity between 0.01 and 0.06 BTC
        
        return Order(
            price=price,
            quantity=qty,
            side=side,
            order_type=OrderType.LIMIT 
        )