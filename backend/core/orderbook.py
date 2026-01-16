import heapq
from typing import List, Optional, Dict
from backend.core.datatypes import Order, Side

class OrderBook:
    def __init__(self):
        # The Heaps: Keep orders sorted automatically
        self.bids: List[Order] = [] 
        self.asks: List[Order] = []
        
        # The Dictionary: Maps order_id -> Order
        # Used for O(1) lookups and cancellations
        self._orders: Dict[str, Order] = {}

    def add(self, order: Order):
        """
        Adds an order to the book.
        Time Complexity: O(log N) due to heap push.
        """
        self._orders[order.id] = order
        
        if order.side == Side.BUY:
            heapq.heappush(self.bids, order)
        else:
            heapq.heappush(self.asks, order)

    def cancel(self, order_id: str):
        """
        Cancels an order.
        Time Complexity: O(1) - "Lazy Deletion"
        We remove it from the dict, but leave it in the heap.
        It will be cleaned up when it reaches the top.
        """
        if order_id in self._orders:
            del self._orders[order_id]

    def get_best_bid(self) -> Optional[Order]:
        """
        Returns the highest buy order.
        Cleans up 'dead' (cancelled) orders from the top of the heap.
        """
        while self.bids:
            # Peek at the top order
            best_order = self.bids[0]
            
            # If it's not in our dict, it was cancelled. Pop and discard.
            if best_order.id not in self._orders:
                heapq.heappop(self.bids)
                continue
                
            return best_order
        return None

    def get_best_ask(self) -> Optional[Order]:
        """
        Returns the lowest sell order.
        Cleans up 'dead' (cancelled) orders from the top of the heap.
        """
        while self.asks:
            best_order = self.asks[0]
            
            if best_order.id not in self._orders:
                heapq.heappop(self.asks)
                continue
                
            return best_order
        return None

    def remove_best_bid(self):
        """Removes the top bid from the heap (after a trade)."""
        if self.bids:
            order = heapq.heappop(self.bids)
            # Also remove from dict if it exists
            if order.id in self._orders:
                del self._orders[order.id]

    def remove_best_ask(self):
        """Removes the top ask from the heap (after a trade)."""
        if self.asks:
            order = heapq.heappop(self.asks)
            if order.id in self._orders:
                del self._orders[order.id]