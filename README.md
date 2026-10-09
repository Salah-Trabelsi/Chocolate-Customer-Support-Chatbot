# Chocolate Customer Support Chatbot

An AI customer support chatbot for a chocolate shop with:
- Text chat (React + FastAPI + LangGraph)
- Tool-driven order and payment workflows
- Voice chat (Pipecat + WebRTC + OpenAI STT/TTS)
- PostgreSQL persistence for customers, orders, and payments
- ChromaDB semantic retrieval for FAQ and product inventory

## What This Project Does

The assistant can:
- Answer FAQs (delivery, returns, policies, allergens, and more)
- Recommend products from inventory
- Filter products by price and currency
- Create customer profiles
- Place orders
- Verify customer identity for order/payment security
- Process payments

The project uses PostgreSQL for customer, order, and payment data. FAQ and product inventory data are stored in JSON files and indexed in ChromaDB for semantic retrieval.

The inventory JSON file is also used as the current source of truth for product prices and stock quantities during the prototype phase

## Tech Stack

- Backend: FastAPI, LangGraph, LangChain, ChromaDB, SQLAlchemy
- Database: PostgreSQL
- Database UI: Adminer
- Frontend: React + Vite
- Voice: Pipecat WebRTC transport, OpenAI STT, OpenAI TTS
- LLM: OpenAI chat model with tool calling
- DevOps: Docker Compose

## Architecture Overview

```mermaid
flowchart TD
    U[User] --> FE[React Frontend]
    FE -->|POST /api/chat/ask| BE[FastAPI Backend]
    BE --> CS[Chat Service]
    CS --> LG[LangGraph Agent]
    LG --> TN[Tool Node]

    TN --> VS[(ChromaDB Vector Store)]
    TN --> INV[(inventory.json)]
    TN --> PG[(PostgreSQL)]

    FAQ[FAQ.json] --> VS
    INV --> VS

    PG --> CUST[customers]
    PG --> ORD[orders + order_items]
    PG --> PAY[payments]

    LG --> BE
    BE --> FE
```

## How The Agent and Tools Work

The chatbot is implemented as a LangGraph loop:

1. The agent receives conversation messages.
2. The model decides whether to answer directly or call tools.
3. If tools are needed, execution moves to a tool node.
4. Tool outputs are fed back into the agent.
5. The loop continues until the model returns a final answer.

Tools cover:

- FAQ retrieval from ChromaDB vector search
- Product recommendation using ChromaDB semantic inventory search
- Product price filtering using fresh inventory JSON data
- Customer profile creation using PostgreSQL
- Customer data protection checks using PostgreSQL
- Order creation and order verification using PostgreSQL
- Payment processing using PostgreSQL
- Stock quantity updates using inventory JSON

This setup gives predictable business actions while still allowing natural conversation. ChromaDB is used for semantic search, PostgreSQL is used for customer/order/payment persistence, and `inventory.json` remains the current source of truth for product prices and stock.

## Voice Mode (Pipecat) Flow

Voice mode uses a dedicated Pipecat pipeline:

1. User clicks the mic button in the frontend.
2. Frontend connects to Pipecat start endpoint (default: http://localhost:7860/start).
3. Audio is streamed over WebRTC.
4. OpenAI STT transcribes user speech.
5. A LangGraph-based LLM service generates a response.
6. OpenAI TTS converts response text to speech.
7. Audio is streamed back to the browser.

The voice LLM layer applies voice-friendly response formatting (shorter, non-Markdown output, clear pricing language).

## Prerequisites

- Python 3.10+
- Node.js 18+
- Docker Desktop
- An OpenAI API key

## Environment Variables

Create a .env file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql+psycopg://chocowise_user:chocowise_password@127.0.0.1:5433/chocowise
```

Optional frontend environment variables (in frontend/chocolateApp-frontend/.env):

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_VOICE_API_URL=http://localhost:7860/start
```


## Run PostgreSQL With Docker

The project uses Docker Compose to run PostgreSQL and Adminer locally.

PostgreSQL is used for:

- customers
- orders
- order_items
- payments

Adminer is used as a simple browser UI to inspect the database.

### 1. Start Docker Desktop

Make sure Docker Desktop is running.

### 2. Start PostgreSQL and Adminer

From the project root, run:

```bash
docker compose up -d
```

This starts the PostgreSQL and Adminer containers defined in `docker-compose.yml`.

### 3. Check Running Containers

```bash
docker ps
```

You should see containers similar to:

```txt
chocowise-postgres
chocowise-adminer
```

### 4. PostgreSQL Connection

PostgreSQL runs inside Docker on port `5432`, but it is exposed on the host machine through port `5433`.

The backend connects to PostgreSQL using this value in `.env`:

```env
DATABASE_URL=postgresql+psycopg://chocowise_user:chocowise_password@127.0.0.1:5433/chocowise
```

### 5. Open Adminer

Adminer is available at:

```txt
http://localhost:8080
```

Login with:

```txt
System: PostgreSQL
Server: postgres
Username: chocowise_user
Password: chocowise_password
Database: chocowise
```

Important:

- In Adminer, use `postgres` as the server name.
- In the Python `.env`, use `127.0.0.1:5433`.

### 6. Create Database Tables

After PostgreSQL is running, create the database tables:

```bash
python -m app.domains.chat.repositories.init_db
```

This creates:

- customers
- orders
- order_items
- payments

### 7. Optional: Migrate Existing JSON Data

If you have existing prototype data in JSON files, migrate it into PostgreSQL:

```bash
python -m app.domains.chat.repositories.migrate_json_to_postgres
```

This imports:

- customer data into `customers`
- order data into `orders`
- order item data into `order_items`
- payment data into `payments`

This migration is intended for local development and prototype setup.


## Run Backend (Text Chat API)

From the project root:

```bash
pip install -r requirments.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend base URL:
- http://localhost:8000

API endpoint used by frontend:
- POST http://localhost:8000/api/chat/ask

## Run Voice Bot Server (Pipecat)

From the project root in a separate terminal:

```bash
python -m app.domains.chat.voice -t webrtc
```

This starts the Pipecat voice bot entrypoint used by the frontend mic feature.

## Run Frontend

From frontend/chocolateApp-frontend:

```bash
npm install
npm run dev
```

Frontend URL:
- http://localhost:5173

## Recommended Local Startup Order

1. Start FastAPI backend on port 8000.
2. Start Pipecat voice bot process.
3. Start React frontend and open http://localhost:5173.

## Project Data Files

Business data is read/written from JSON files in the root folder:
- customers_database.json
- inventory.json
- orders_database.json
- payments_database.json
- FAQ.json

Vector data is persisted under chroma_db.

## Troubleshooting

- If text chat fails, confirm backend is running on port 8000.
- If voice chat fails to connect, confirm Pipecat process is running and frontend VITE_VOICE_API_URL matches.
- If model/tool calls fail, confirm OPENAI_API_KEY is set in .env.
- If CORS errors appear, run frontend on localhost:5173 or update backend CORS settings.

## Notes

- The requirements file is named requirments.txt in this repository.
- The frontend folder name contains componenets as currently implemented.
