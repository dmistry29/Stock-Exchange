import asyncio
import json
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from backend.core.orderbook import OrderBook

class ExchangeServer:
    def __init__(self, orderbook: OrderBook):
        self.orderbook = orderbook
        self.app = FastAPI()
        self.active_connections: List[WebSocket] = []

        # 1. Enable CORS (Critical for React Frontend)
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, specify "http://localhost:3000"
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # 2. Setup Routes
        self.app.websocket("/ws")(self.websocket_endpoint)
        self.app.get("/")(self.read_root)

    async def read_root(self):
        """Health check endpoint."""
        return {"status": "online", "bids": len(self.orderbook.bids), "asks": len(self.orderbook.asks)}

    async def websocket_endpoint(self, websocket: WebSocket):
        """
        The Stream: Accepts connections and pushes data.
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        try:
            while True:
                # Keep the connection open.
                # In a real app, you might listen for "Buy" commands from the UI here.
                await websocket.receive_text()
        except WebSocketDisconnect:
            self.active_connections.remove(websocket)

    async def broadcast(self):
        """
        Push the current Order Book state to all connected frontends.
        Run this in a loop from main.py.
        """
        if not self.active_connections:
            return

        # Prepare the snapshot (Top 20 Bids/Asks for visualization)
        # Note: We convert dataclasses to dicts/JSON here
        snapshot = {
            "bids": [{"price": abs(o.price), "qty": o.quantity} for o in self.orderbook.bids[:20]],
            "asks": [{"price": o.price, "qty": o.quantity} for o in self.orderbook.asks[:20]]
        }
        
        message = json.dumps(snapshot)
        
        # Broadcast to all
        # We iterate over a copy [:] to avoid issues if a connection drops during iteration
        for connection in self.active_connections[:]:
            try:
                await connection.send_text(message)
            except:
                self.active_connections.remove(connection)

    def get_app(self):
        """Returns the FastAPI app instance for Uvicorn to run."""
        return self.app