import asyncio
import json
import websockets
from typing import Dict
from backend.core.datatypes import Order, Side, OrderType
from backend.core.orderbook import OrderBook

class CoinbaseClient:
    def __init__(self, orderbook: OrderBook):
        self.orderbook = orderbook
        self.uri = "wss://advanced-trade-ws.coinbase.com"
        # We need to track 'Price -> OrderID' to update/cancel specific levels
        # Format: { "buy": { price: order_id }, "sell": { price: order_id } }
        self.active_orders: Dict[str, Dict[float, str]] = {
            "buy": {},
            "sell": {}
        }

    async def connect(self):
        """Connects to Coinbase and ingests the Firehose."""
        print(f"Connecting to Coinbase Public Feed ({self.uri})...")
        async with websockets.connect(self.uri, max_size=None) as ws:
            # Subscribe to the 'level2' channel (The Order Book)
            subscribe_message = {
                "type": "subscribe",
                "product_ids": ["BTC-USD"],
                "channel": "level2"
            }
            await ws.send(json.dumps(subscribe_message))
            
            while True:
                try:
                    response = await ws.recv()
                    data = json.loads(response)
                    
                    if data.get("channel") != "l2_data":
                        continue
                        
                    events = data.get("events", [])
                    for event in events:
                        # Handle the initial "Snapshot" (The full book state)
                        if event["type"] == "snapshot":
                            self._process_updates(event["updates"])
                            print("Snapshot loaded! Engine is hot.")
                        
                        # Handle real-time updates
                        elif event["type"] == "update":
                            self._process_updates(event["updates"])
                            
                except Exception as e:
                    print(f"Coinbase Error: {e}")
                    # In a real interview, you'd implement exponential backoff here
                    await asyncio.sleep(5) 

    def _process_updates(self, updates):
        """
        Translates Coinbase 'Level 2 Updates' into our 'Order' objects.
        """
        for update in updates:
            side_str = update["side"] # "bid" or "offer"
            price = float(update["price_level"])
            new_quantity = float(update["new_quantity"])
            
            # Map Coinbase "offer" to our "sell" enum
            side = Side.BUY if side_str == "bid" else Side.SELL
            
            # 1. Cancel the OLD order at this price level (if it exists)
            # We look up the ID we generated previously
            side_key = "buy" if side == Side.BUY else "sell"
            old_order_id = self.active_orders[side_key].get(price)
            
            if old_order_id:
                self.orderbook.cancel(old_order_id)
            
            # 2. If quantity is 0, it's a deletion. We are done.
            if new_quantity == 0:
                if old_order_id:
                    del self.active_orders[side_key][price]
                continue
            
            # 3. Create the NEW order reflecting the update
            new_order = Order(
                price=price,
                quantity=new_quantity,
                side=side,
                order_type=OrderType.LIMIT
            )
            
            # 4. Add to Engine and update our map
            self.orderbook.add(new_order)
            self.active_orders[side_key][price] = new_order.id