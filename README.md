# LLM-Evaluator-FastAPI

## Homepage

![Homepage](https://github.com/user-attachments/assets/caddcd0e-36d6-4b22-acaf-788284600163)

## Chat Page

![Chat Page](https://github.com/user-attachments/assets/4f4103d0-4ba3-4bd5-a21c-ccddb9e3b397)

## User Dashboard

![User Dashboard](https://github.com/user-attachments/assets/bb2707ce-d069-4fc6-8781-fc94506ec794)

FastAPI-based web application that combines an e-commerce support chatbot with multi-model LLM benchmarking. Users can chat with different LLM providers (Groq, Gemini, Mistral, OpenRouter), rate responses, and view daily and weekly leaderboards. Built with FastAPI (async), PostgreSQL, SQLAlchemy, JWT authentication, and cookies.

---

## Features

### Authentication
- User registration with unique username and email  
- Login using email or username  
- Password hashing using bcrypt  
- JWT token generated on login (valid for 60 minutes)  
- Token stored in HTTP-only cookies  
- Token automatically sent with each request  
- Server verifies JWT on every protected route  
- Change username and password  
- Logout support  

### FAQ-Based Chatbot
- E-commerce support persona  
- FAQ data loaded from CSV  
- FAQ content injected into system prompt  
- Strict prompt constraints to reduce hallucination  
- Fallback response if answer not found  
- Per-user, per-model conversation memory (in-memory storage)  
- Automatic cleanup of expired sessions  

### Multi-Model Support
- Switch between different LLM providers  
- Ask the same question to multiple models  
- Dynamic model mapping system  

Supported providers:
- Groq  
- Google Gemini  
- Mistral  
- OpenRouter (DeepSeek, OLMo, Nvidia, etc.)  

### Rating System
- Rate responses from 0–10  
- Ratings stored in PostgreSQL  
- Each rating linked to user and model  
- Automatic timestamping  

### Leaderboards
- Top models (last 24 hours)  
- Top models (last 7 days)  
- Average score calculation per model  
- Sorted by highest rating  

### Account Section
- View personal ratings  
- Change username  
- Change password  

---

## Tech Stack

Backend:
- FastAPI (async)  
- PostgreSQL  
- SQLAlchemy (Async ORM)  

Frontend:
- Jinja2 templates (server-side rendering)  
- HTML, CSS, JavaScript  

Authentication:
- JWT (HS256)  
- HTTP-only cookies  

External APIs:
- Groq  
- Gemini  
- Mistral  
- OpenRouter  

---

## Setup

1. Install requirements

```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root and add:

```env
GROQ_API_KEY=your_groq_api_key
MISTRAL_API_KEY=your_mistral_api_key
GEMINI_API_KEY=your_gemini_api_key
OPEN_ROUTER_API_KEY=your_openrouter_api_key
LLAMA_API_KEY=your_llama_api_key
POSTGRES_PASS=your_postgres_password
SECRET_KEY=your_secret_key
```

3. Run the application

```bash
python main.py
```

---

## Notes

- API keys and secrets are stored in environment variables and not included in the repository.  
- JWT tokens expire after 60 minutes.  
- Conversation history is stored in memory and cleared when the token expires.  
