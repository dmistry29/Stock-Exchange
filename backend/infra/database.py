import asyncio
import aiosqlite
from backend.core.datatypes import Trade

class TradeDatabase:
    def __init__(self, db_name="data/trade_history.db"):
        self.db_name = db_name
        self.queue = asyncio.Queue()
        self.running = False

    async def start(self):
        """Initializes the DB and starts the background writer."""
        self.running = True
        
        # 1. Initialize Database
        async with aiosqlite.connect(self.db_name) as db:
            # WAL Mode for performance
            await db.execute("PRAGMA journal_mode=WAL;")
            
            # Create Table if it doesn't exist
            await db.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    trade_id TEXT PRIMARY KEY,
                    price REAL,
                    quantity REAL,
                    buyer_order_id TEXT,
                    seller_order_id TEXT,
                    timestamp REAL
                )
            """)
            await db.commit()

        # 2. Start the Background Worker
        asyncio.create_task(self._writer_worker())
        print(f"Database {self.db_name} connected (WAL mode enabled).")

    async def add_trade(self, trade: Trade):
        """
        Non-blocking add. Puts trade in memory queue and returns immediately.
        """
        await self.queue.put(trade)

    async def _writer_worker(self):
        """
        The Background Worker: Pulls from queue -> Writes to Disk.
        """
        while self.running:
            trade = await self.queue.get()
            
            async with aiosqlite.connect(self.db_name) as db:
                await db.execute("""
                    INSERT INTO trades (trade_id, price, quantity, buyer_order_id, seller_order_id, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    trade.trade_id, 
                    trade.price, 
                    trade.quantity, 
                    trade.buyer_order_id, 
                    trade.seller_order_id, 
                    trade.timestamp
                ))
                await db.commit()
            
            self.queue.task_done()