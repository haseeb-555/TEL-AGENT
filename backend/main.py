from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
import requests, atexit
from config.database import users

from routes.user import user_router
from routes.events import event_router
from routes.agents import agent_router
from routes.emails import email_router

app = FastAPI()
app.include_router(user_router)
app.include_router(event_router)
app.include_router(agent_router)
app.include_router(email_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

def get_all_user_emails():
    return [user["email"] for user in users.find({}, {"email": 1, "_id": 0})]

def schedule_events():
    print("Scheduling events...")
    try:
        emails = get_all_user_emails()
        for email in emails:
            res = requests.post("http://localhost:8000/createEvents", json={"email": email})
            print(f"Scheduled for {email}, status: {res.status_code}")
    except Exception as e:
        print("Error calling createEvents:", e)

scheduler = BackgroundScheduler()
scheduler.add_job(schedule_events, 'interval', hours=2)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())
