# 📬 TEL-AGENT – Your Smart Email Reminder System

> Never miss a deadline again!

## 🚩 Problem Statement

As students, we've often faced the frustrating experience of missing out on company application deadlines, exam schedules, or exciting contests and hackathons – simply because we overlooked important emails.  
Personally, and among my friends, we've lost chances to appear for exams, apply for dream roles, and some even had to face credit deductions for missing exams due to no reminders.

## 💡 Our Solution

To solve this, we built **TEL-AGENT** – an automated Email Reminder System using the **Google Agent Development Kit (ADK)** and **FastAPI**.  
This smart assistant scans your emails, extracts relevant events (like deadlines, contests, exams, and applications), and pushes reminders to your Google Calendar so you never miss out again.

## ⚙️ Tech Stack

- **Google Agent Development Kit (ADK)**
- **FastAPI**
- **Google OAuth & Gmail API**
- **Google Calendar API**
- **LLM Agents** for email classification and deadline extraction

## 🧠 Features

- 🔍 Scans Gmail inbox using Google API
- 🧠 Uses LLM agents to classify emails based on their content (e.g., contests, exams, job deadlines)
- 🗓️ Extracts relevant details and automatically adds reminders to your **Google Calendar**
- 🛡️ Secure authentication via Google OAuth
- 💡 Intelligent resource suggestions for each event type

## 📁 Project Structure

TEL-AGENT/
├── backend/
│   ├── agents/               # Google ADK-based agents (contest, company, etc.)
│   ├── static/
│   ├── utils/                # Email parsing, token helpers, etc.
│   ├── main.py               # FastAPI server entrypoint
│   ├── test.py               # Test scripts
│   ├── .env                  # Server-side secrets
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   ├── src/                  # React source code
│   ├── .env                  # React environment variables
│   ├── vite.config.js
│   ├── package.json
│   └── index.html
│
├── .env                      # Global config (if needed)
└── README.md                 # This file

## ⚙️ Tech Stack

| Layer        | Technologies Used                                                                 |
|--------------|-----------------------------------------------------------------------------------|
| Frontend     | React + Vite                                                                      |
| Backend      | FastAPI, Gmail API, Google Calendar API                                           |
| AI/Agents    | Google Agent Development Kit (ADK) (RouterAgent, LoopAgent, ParallelAgent, etc.)  |
| Auth/OAuth   | Google OAuth 2.0                                                                  |
| Intelligence | LLM Agents for email classification & data extraction                             |


## 🔑 Google Cloud Setup
# 🔧 OAuth Credentials

1. Go to Google Cloud Console
2. Create a project → OAuth Consent Screen
3. App type: External, Test User: your email
4. Scopes:
  https://www.googleapis.com/auth/userinfo.email
  https://www.googleapis.com/auth/gmail.readonly
  https://www.googleapis.com/auth/calendar
5. Create OAuth 2.0 Client ID:
  App type: Web
  Redirect URI: http://localhost:3000/oauth2callback


## 🚀 Getting Started

1. Clone the Repo
  git clone [(https://github.com/haseeb-555/TEL-AGENT.git)]
  cd TEL-AGENT
2. Backend Setup (FastAPI + ADK)
   cd backend
     python -m venv venv
     # Mac / Linux
      source .venv/bin/activate
     # Windows CMD:
      .venv\Scripts\activate.bat
     # Windows PowerShell:
      .venv\Scripts\Activate.ps1
     pip install -r requirements.txt
  Create .env in backend/:
    GOOGLE_CLIENT_ID=your-client-id
    GOOGLE_CLIENT_SECRET=your-client-secret
    REDIRECT_URI=http://localhost:3000
    SECRET_KEY=your-fastapi-secret
  Run the server:
    uvicorn main:app --reload
  API running at http://localhost:8000

3. Frontend Setup (React + Vite)
  cd frontend
  npm install
Create .env in frontend/:
  VITE_GOOGLE_CLIENT_ID=your-client-id
  VITE_BACKEND_URL=http://localhost:8000
Run the frontend:
  npm run dev
App running at: http://localhost:3000


## 🔄 OAuth2 Flow

User clicks Login with Google
Google redirects to http://localhost:3000/oauth2callback
Frontend captures code and sends it to backend /auth/callback
Backend exchanges code for access token
Gmail API fetches recent emails
AI agents parse, classify, and suggest resources
Events added to Google Calendar

## 🤖 Agents (Google ADK)

Each email is processed through a RouterAgent, which forwards it to relevant sub-agents like:
ContestAgent → coding contest info
CompanyAgent → interview/event info
TravelAgent, MedicalAgent, etc.
Agents extract:
Event type, description
Time, platform, deadlines
Resources (YouTube/blogs via Google Search)
