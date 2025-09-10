# backend/app.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
IBM_GRANITE_API_KEY = os.getenv("IBM_GRANITE_API_KEY")

# FastAPI app
app = FastAPI(
    title="Personal Finance Chatbot Backend",
    description="Provides financial advice via HuggingFace and IBM Granite models",
    version="1.0.0",
)

# Allow frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request model ---
class ChatRequest(BaseModel):
    user_id: str
    occupation: str
    age: int
    income_monthly: float
    expenses: dict
    prompt_source: str

# --- Root endpoint ---
@app.get("/")
def read_root():
    return {"message": "Personal Finance Chatbot Backend is running!"}

# --- Chat endpoint ---
@app.post("/chat")
def chat(request: ChatRequest):
    # Extract data
    occupation = request.occupation
    age = request.age
    income = request.income_monthly
    expenses = request.expenses
    prompt_source = request.prompt_source

    total_expenses = sum(expenses.values())
    savings = income - total_expenses

    # Build summary text
    summary = f"Hello! As a {occupation}, your total monthly expenses are ₹{total_expenses:.2f}, " \
              f"and you can save ₹{savings:.2f} per month."

    # Optional: send summary to HuggingFace or IBM Granite if needed
    if prompt_source == "hf" and HUGGINGFACE_API_KEY:
        try:
            hf_api_url = "https://api-inference.huggingface.co/models/gpt2"
            hf_headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
            payload = {"inputs": summary}
            response = requests.post(hf_api_url, headers=hf_headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            hf_summary = data[0]['generated_text'] if isinstance(data, list) else str(data)
            summary = hf_summary
        except Exception as e:
            summary += f" (HuggingFace fetch failed: {e})"

    return {"summary": summary, "details": expenses}
