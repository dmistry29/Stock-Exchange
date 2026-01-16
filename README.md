# Real-Time Cryptocurrency Matching Engine

A high-performance, full-stack trading system that ingests live Bitcoin (BTC-USD) data from Coinbase, maintains an internal Limit Order Book (LOB), and executes trades using a price-time priority matching algorithm. The system features a real-time React dashboard to visualize market depth and trade execution.

## Features

* **Real-Time Ingestion:** WebSocket client (`asyncio`) consuming the Coinbase Pro `level2` channel.
* **Matching Engine:** Custom Limit Order Book implementation using **dual binary heaps** for O(log n) order matching.
* **Trade Execution:** Automated trading bot that identifies spread crossing opportunities and executes orders.
* **Persistence:** Asynchronous SQLite storage using a "fire-and-forget" queue pattern to prevent I/O blocking.
* **Visualization:** React frontend with real-time Depth Charts (Cumulative Volume) and Order Book tape.

## Tech Stack

* **Backend:** Python 3.10+, FastAPI, Asyncio, Websockets, SQLite (aiosqlite)
* **Frontend:** React.js, Recharts, WebSocket API
* **Architecture:** Event-driven microservices (Ingestion, Engine, Persistence)

---

## Prerequisites

Before running the project, ensure you have the following installed:
* **Python 3.8+**
* **Node.js & npm** (for the frontend)

---

## Installation & Setup

### Run the project
```bash

Follow the steps below 

git clone [https://github.com/dmistry29/Stock-Exchange.git](https://github.com/dmistry29/Stock-Exchange.git)
cd Stock-Exchange

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install fastapi "uvicorn[standard]" websockets aiosqlite

cd frontend
npm install
cd ../

# This starts the Ingestion Service, Matching Engine, and WebSocket Server
python -m backend.main

cd frontend
npm start
