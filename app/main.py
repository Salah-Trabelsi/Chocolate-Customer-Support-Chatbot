from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router


app = FastAPI(
    title="Chocolate Customer Support API",
    description="FastAPI backend for the Chocolate Shop AI chatbot.",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Chocolate Customer Support API is running 🍫"
    }


app.include_router(
    api_router,
    prefix="/api",
)