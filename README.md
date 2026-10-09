# ChocoWise — AI Customer Support Chatbot

ChocoWise is an AI customer support assistant for a demo chocolate shop. It answers questions, recommends products, and guides customers through profile creation, ordering, and simulated payments through text or voice.

**Status:** Personal project under active development.

> Payments are simulated. No real payment provider is connected and no money is transferred. Delivery selection is not yet implemented.

## Features

- Semantic FAQ search for questions about delivery policies, returns, allergens, and more
- Product recommendations based on natural-language requests
- Product filtering by price and currency
- Customer profile creation directly in the conversation
- Simplified matching against existing demo customer profiles
- Retrieval of existing customer orders
- Order placement with product availability and stock checks
- Stock updates after order placement
- Simulated payments and order status updates
- Voice conversations with speech-to-text and text-to-speech
- Voice transcripts displayed in the chat interface

## Tech Stack

| Area | Technologies |
| --- | --- |
| Frontend | React, Vite |
| Backend | Python, FastAPI |
| AI Agent | LangGraph, LangChain, OpenAI tool calling |
| Semantic Search | ChromaDB |
| Database | PostgreSQL, SQLAlchemy |
| Voice | Pipecat, WebRTC, OpenAI STT, OpenAI TTS |
| Local Database Environment | Docker Compose, Adminer |

Docker Compose currently runs PostgreSQL and Adminer. The frontend, FastAPI backend, and Pipecat voice server run separately.

## Architecture Overview

The React frontend sends text messages to FastAPI. A chat service passes the conversation to a LangGraph agent, which decides whether to answer directly or call a tool.

Tools retrieve information or perform application actions. Their results return to the agent, which generates the response.

```mermaid
flowchart TD
    FE[React Frontend] -->|POST /api/chat/ask| BE[FastAPI Backend]
    BE --> CS[Chat Service]
    CS --> LG[LangGraph Agent]
    LG -->|Tool calls| TN[Tool Node]
    TN -->|Tool results| LG

    TN -->|Semantic retrieval| VS[(ChromaDB)]
    TN -->|Prices and stock| INV[inventory.json]
    TN -->|Customers, orders and payments| PG[(PostgreSQL)]

    FAQ[FAQ.json] -.->|Indexing| VS
    INV -.->|Indexing| VS

    LG -->|Final response| CS
    CS --> BE
    BE --> FE
```

The diagram shows the text-chat workflow. Voice conversations use a dedicated Pipecat pipeline connected to the LangGraph-based chatbot logic.

## How the Agent and Tools Work

The chatbot follows a LangGraph agent loop:

1. The agent receives the conversation messages.
2. The OpenAI model decides whether to answer directly or request tools.
3. Requested tools execute in a tool node.
4. Tool results are returned to the agent.
5. The loop continues until the agent produces a final response.

### Available Tools

| Tool | Purpose |
| --- | --- |
| `query_knowledge_base` | Retrieve relevant FAQ content from ChromaDB |
| `search_for_product_recommendations` | Find products through semantic search |
| `filter_products_by_price` | Filter current inventory by price and currency |
| `data_protection_check` | Match supplied details against demo customer profiles |
| `create_new_customer` | Create a customer profile in PostgreSQL |
| `retrieve_existing_customer_orders` | Retrieve an existing customer's orders |
| `place_order` | Check inventory, save an order and its items, and update stock |
| `verify_customer_and_order` | Check the association between a customer and an order |
| `process_payment` | Simulate a payment, save the payment record, and update order status |

Customer detail matching is a simplified demo workflow. It is not a replacement for authentication or production identity verification.

## Data Storage

The application separates semantic retrieval from operational data.

### Semantic Search

- `FAQ.json` supplies FAQ content for indexing into ChromaDB.
- `inventory.json` supplies product content for semantic product indexing.
- FAQ and product recommendation tools query ChromaDB during conversations.
- ChromaDB vector data is persisted under `chroma_db/`.

The FAQ retrieval tool searches ChromaDB rather than reading `FAQ.json` directly during each conversation.

### Product Inventory

During the prototype phase, `inventory.json` remains the source of truth for:

- Product prices
- Currency
- Stock quantities
- Product availability
- Stock updates after order placement

Semantic search helps discover relevant products. Price filtering and order checks use the current inventory data.

### PostgreSQL

SQLAlchemy repositories handle persistence for:

- `customers`
- `orders`
- `order_items`
- `payments`

Payment records represent simulated payments only.

Customers, orders, and payments were previously stored in JSON files. Those files are no longer part of the active chatbot workflow.

## Example Ordering Workflow

1. A customer asks for a product or recommendation.
2. The agent calls a product search or filtering tool.
3. ChromaDB supports semantic discovery, while inventory data provides current prices and stock.
4. The customer supplies details to match an existing demo profile or create a new profile.
5. The agent calls `place_order`.
6. The tool checks availability, saves the order and its items in PostgreSQL, and updates stock in `inventory.json`.
7. The assistant presents an order summary.
8. The customer selects a payment method for the simulation.
9. The agent checks the customer–order association and calls `process_payment`.
10. A simulated payment record is saved in PostgreSQL, and the order status is updated to `Paid`.

Currency conversions use a configured demo exchange rate, not live exchange-rate data.

## Voice Mode

Voice mode uses a dedicated Pipecat pipeline:

1. The user clicks the microphone button in the frontend.
2. The frontend connects to the Pipecat start endpoint.
3. Audio is streamed over WebRTC.
4. OpenAI speech-to-text transcribes the user's speech.
5. A LangGraph-based service handles the request and calls tools when needed.
6. OpenAI text-to-speech converts the response into audio.
7. Audio is streamed back to the browser, with transcripts displayed in the chat interface.

The voice response format is adapted for speech: shorter answers, no Markdown, and clear spoken pricing.

Default voice endpoint:

```text
http://localhost:7860/start
```

## Prerequisites

- Python and Node.js versions compatible with the repository's dependencies
- npm
- Docker Desktop, or Docker Engine with the Compose plugin
- An OpenAI API key
- Microphone access for voice mode

## Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Salah-Trabelsi/Chocolate-Customer-Support-Chatbot.git
cd Chocolate-Customer-Support-Chatbot
```

### 2. Create a Python Virtual Environment

From the project root:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```bash
source .venv/bin/activate
```

Install the Python dependencies:

```bash
python -m pip install -r requirments.txt
```

The filename `requirments.txt` matches the current repository spelling.

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql+psycopg://chocowise_user:chocowise_password@127.0.0.1:5433/chocowise
```

The database credentials shown here are for local development and must match your Docker Compose configuration.

Optional frontend environment variables can be configured in `frontend/chocolateApp-frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_VOICE_API_URL=http://localhost:7860/start
```

Keep real API keys and local `.env` files out of version control.

### 4. Start PostgreSQL and Adminer

Start Docker, then run this command from the project root:

```bash
docker compose up -d
```

This starts the PostgreSQL and Adminer services defined in `docker-compose.yml`.

Check the running containers:

```bash
docker compose ps
```

Expected container names include:

```text
chocowise-postgres
chocowise-adminer
```

PostgreSQL uses port `5432` inside Docker and is exposed on host port `5433`.

The locally running backend connects through:

```text
127.0.0.1:5433
```

### 5. Create Database Tables

With PostgreSQL running and the Python environment activated:

```bash
python -m app.domains.chat.repositories.init_db
```

This creates the application tables:

- `customers`
- `orders`
- `order_items`
- `payments`

### 6. Initialize ChromaDB

FAQ and product collections must be populated before semantic search can return results.

Source files:

- `FAQ.json`
- `inventory.json`

Persistent vector storage:

```text
chroma_db/
```

**Documentation TODO:** Add the repository's exact indexing command here, or document automatic initialization if the application performs indexing at startup.

### 7. Optional: Migrate Previous JSON Data

If you have customer, order, and payment data from the earlier JSON-based prototype:

```bash
python -m app.domains.chat.repositories.migrate_json_to_postgres
```

This imports existing prototype data into:

- `customers`
- `orders`
- `order_items`
- `payments`

This step is intended for migrating an existing local setup. It is not required for a fresh installation without previous business data.

## Run the Application

Use separate terminals for the backend, voice server, and frontend. Activate the Python virtual environment in each Python terminal.

### Text Chat Backend

From the project root:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend URL:

```text
http://localhost:8000
```

Text-chat endpoint:

```text
POST http://localhost:8000/api/chat/ask
```

### Voice Server

For voice interaction, run this in a separate terminal from the project root:

```bash
python -m app.domains.chat.voice -t webrtc
```

The frontend uses the Pipecat start endpoint configured through `VITE_VOICE_API_URL`.

### Frontend

From the project root:

```bash
cd frontend/chocolateApp-frontend
npm install
npm run dev
```

Default frontend URL:

```text
http://localhost:5173
```

### Startup Order

After completing the initial setup:

1. Start PostgreSQL and Adminer with `docker compose up -d`.
2. Start the FastAPI backend.
3. Start the Pipecat server if using voice mode.
4. Start the React frontend.

## Inspect the Database with Adminer

Open:

```text
http://localhost:8080
```

Use the local development connection details:

```text
System: PostgreSQL
Server: postgres
Username: chocowise_user
Password: chocowise_password
Database: chocowise
```

Adminer connects to PostgreSQL through the Docker service name `postgres`. The backend runs on the host machine and uses `127.0.0.1:5433`.

## Current Limitations

- Payments are simulated; no real payment provider is integrated.
- Delivery selection is not implemented.
- Customer profile matching is a demo mechanism, not production authentication.
- Product inventory remains JSON-based.
- Inventory updates and PostgreSQL order writes are not covered by one shared database transaction.
- Currency conversion uses a configured demo exchange rate.
- The project is under active development and is not production-ready.

## Planned Improvements

- Automated tests for tools, APIs, and conversation workflows
- Alembic database migrations
- Authentication and authorization
- Admin pages for products and orders
- Real payment-provider integration
- Delivery selection
- Further improvements to tool descriptions and token usage

## Troubleshooting

### Text Chat Is Not Working

- Confirm the FastAPI backend is running on port `8000`.
- Check `VITE_API_BASE_URL`.
- Confirm `OPENAI_API_KEY` is configured.
- Inspect the backend terminal for errors.

### Semantic Search Returns No Results

- Confirm the FAQ and product collections have been indexed.
- Check that the application uses the expected `chroma_db/` storage location.
- Confirm the source files contain the expected data.

### Database Connection Fails

- Run `docker compose ps` to check the database service.
- Confirm `DATABASE_URL` matches the Docker Compose credentials.
- Use host port `5433` when connecting from the locally running backend.
- Confirm the database tables have been initialized.

### Voice Chat Does Not Connect

- Confirm the Pipecat server is running.
- Check `VITE_VOICE_API_URL`.
- Allow microphone access in the browser.
- Inspect the voice server terminal and browser console for errors.

### Frontend Requests Fail with CORS Errors

- Check the frontend URL shown by Vite.
- Confirm that this origin is allowed in the backend CORS configuration.