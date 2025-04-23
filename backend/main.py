from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.user import user_router
from routes.events import event_router
from routes.agents import agent_router
from routes.emails import email_router

app = FastAPI()
app.include_router(user_router)
app.include_router(event_router)
app.include_router(agent_router)
app.include_router(email_router)

origins = [
    "http://localhost",  
    "http://localhost:3000",  
    "http://127.0.0.1:3000",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)