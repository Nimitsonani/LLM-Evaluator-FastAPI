# LLM-Evaluator-FastAPI

This project is a FastAPI-based web application that does two things:

1. Acts as an e-commerce support chatbot  
2. Lets users compare and rate responses from multiple LLM providers  

Instead of just chatting with one model, users can switch between providers, ask the same question to different models, and rate their responses. The app then builds daily and weekly leaderboards based on those ratings.

---

## What This Project Is

At its core, this is a multi-model LLM evaluation platform with authentication and persistent storage.

Users can:

- Register and log in
- Chat with different LLM providers
- Rate each model’s response
- See which models perform best over time

It combines a support-style chatbot with a simple benchmarking system.

---

## Screenshots

### Homepage

![Homepage](https://github.com/user-attachments/assets/caddcd0e-36d6-4b22-acaf-788284600163)

### Chat Page

![Chat Page](https://github.com/user-attachments/assets/4f4103d0-4ba3-4bd5-a21c-ccddb9e3b397)

### User Dashboard

![User Dashboard](https://github.com/user-attachments/assets/bb2707ce-d069-4fc6-8781-fc94506ec794)

---

## How It Works

### Chat System

- FAQ data is loaded from a CSV file.
- The FAQ content is injected into the system prompt.
- The model is instructed to answer strictly within that scope.
- If the answer is not found in the FAQ context, it returns a fallback response.

Each user has model-specific conversation memory stored in memory.  
Sessions are cleaned up automatically when tokens expire.

---

### Multi-Model Evaluation

The app supports multiple LLM providers:

- Groq  
- Google Gemini  
- Mistral  
- OpenRouter (DeepSeek, OLMo, Nvidia, etc.)

Users can:

- Switch between providers
- Ask identical questions across models
- Compare responses
- Rate each response from 0–10

Each rating is stored in PostgreSQL with:

- User ID  
- Model name  
- Score  
- Timestamp  

---

### Leaderboards

The system calculates:

- Top models in the last 24 hours  
- Top models in the last 7 days  

Average scores are computed per model and sorted automatically.

This allows basic real-time model benchmarking using real user ratings.

---

## Authentication System

- User registration (unique username and email)
- Login using email or username
- Password hashing with bcrypt
- JWT tokens (60-minute expiry)
- Tokens stored in HTTP-only cookies
- JWT verified on every protected route
- Logout support
- Username and password change

Authentication is fully backend-validated — no client-side trust.

---

## Tech Stack

**Backend**
- FastAPI (async)
- PostgreSQL
- SQLAlchemy (async ORM)

**Frontend**
- Jinja2 (server-side rendering)
- HTML / CSS / JavaScript

**Authentication**
- JWT (HS256)
- HTTP-only cookies

**External APIs**
- Groq
- Gemini
- Mistral
- OpenRouter

---

## Running Locally

### Requirements

- Python 3.10+
- PostgreSQL running locally or remotely

### Setup

1. Install dependencies

```
pip install -r requirements.txt
```

2. Create a PostgreSQL database.

3. Create a `.env` file in the root directory:

```
GROQ_API_KEY=your_groq_api_key
MISTRAL_API_KEY=your_mistral_api_key
GEMINI_API_KEY=your_gemini_api_key
OPEN_ROUTER_API_KEY=your_openrouter_api_key
LLAMA_API_KEY=your_llama_api_key
POSTGRES_PASS=your_postgres_password
SECRET_KEY=your_secret_key
```

4. Run the application

```
python main.py
```

---

## Notes

- API keys are stored in environment variables.
- JWT tokens expire after 60 minutes.
- Conversation history is stored in memory and cleared when the session expires.
