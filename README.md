# ChocoWise — AI Customer Support Chatbot

ChocoWise is an AI customer support assistant for a demo chocolate shop. It answers questions, recommends products, and guides customers through profile creation, ordering, and simulated payments through text or voice.


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
