from typing import List
from backend.core.datatypes import Order, Trade, Side
from backend.core.orderbook import OrderBook

def match_order(book: OrderBook, order: Order) -> List[Trade]:
    """
    The Core Matching Algorithm.
    
    Logic:
    1. If it's a BUY order, look for the cheapest SELL (Ask).
    2. If it's a SELL order, look for the most expensive BUY (Bid).
    3. If prices 'cross' (Buy Price >= Sell Price), we trade.
    4. Repeat until the order is filled OR prices no longer cross.
    """
    trades = []

    while order.quantity > 0:
        # 1. Who is the counterparty?
        if order.side == Side.BUY:
            best_match = book.get_best_ask()
            # For a trade to happen, Buyer must pay >= Seller's asking price
            crosses_spread = (best_match and order.price >= best_match.price)
        else:
            best_match = book.get_best_bid()
            # For a trade to happen, Seller must accept <= Buyer's bidding price
            crosses_spread = (best_match and order.price <= best_match.price)

        # 2. Stop if no match is possible
        if not best_match or not crosses_spread:
            break

        # 3. Calculate Trade Quantity (Fill as much as possible)
        # It's the smaller of the two quantities
        fill_qty = min(order.quantity, best_match.quantity)
        
        # 4. Record the Trade
        trade = Trade(
            price=best_match.price, # Trades always happen at the 'resting' price
            quantity=fill_qty,
            buyer_order_id=order.id if order.side == Side.BUY else best_match.id,
            seller_order_id=best_match.id if order.side == Side.BUY else order.id
        )
        trades.append(trade)

        # 5. Update Quantities
        order.quantity -= fill_qty
        best_match.quantity -= fill_qty

        # 6. Clean up the Book
        # If the resting order is fully filled, remove it.
        if best_match.quantity == 0:
            if order.side == Side.BUY:
                book.remove_best_ask()
            else:
                book.remove_best_bid()

    # 7. If the incoming order still has quantity left, add it to the book
    if order.quantity > 0:
        book.add(order)

    return trades