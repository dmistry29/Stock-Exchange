import asyncio
import uvicorn
from backend.core.orderbook import OrderBook
from backend.infra.database import TradeDatabase
from backend.infra.coinbase import CoinbaseClient
from backend.infra.server import ExchangeServer
from backend.bot.trader import TradingBot 

async def broadcast_loop(server: ExchangeServer):
    """
    Push updates to the frontend 50 times a second (50Hz).
    This creates the 'Smooth' real-time feel.
    """
    while True:
        await server.broadcast()
        await asyncio.sleep(0.02)  # 0.02s = 50 FPS

async def main():
    # 1. Initialize the Shared Memory (The Engine)
    print("Initializing Matching Engine...")
    book = OrderBook()

    # 2. Initialize Infrastructure
    db = TradeDatabase()
    client = CoinbaseClient(book)
    server = ExchangeServer(book)
    bot = TradingBot(book, db)

    # 3. Start Database (Background Writer)
    await db.start()

    # 4. Configure Uvicorn (The Web Server)
    # We run it programmatically so it plays nice with our other loops
    config = uvicorn.Config(app=server.get_app(), host="0.0.0.0", port=8000, log_level="info")
    uvicorn_server = uvicorn.Server(config)

    print("System Online. Press Ctrl+C to stop.")

    try:
        # 5. Run Everything Concurrently
        # This is the "Heart" of the application
        await asyncio.gather(
            client.connect(),              # Task A: Ingest Real Data
            uvicorn_server.serve(),        # Task B: Serve Frontend
            broadcast_loop(server),        # Task C: Push Updates
            bot.run()                    # Task D: Run Trading Bot (Step 8)
        )
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())