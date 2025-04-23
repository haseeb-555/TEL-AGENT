from fastapi import APIRouter,HTTPException,Request
from models.user import User
from config.database import users
from schema.schema import individual_serial
from bson import ObjectId
import httpx,os
from dotenv import load_dotenv
from config.config import GOOGLE_TOKEN_URL, GMAIL_API_BASE, USERINFO_URL

load_dotenv()

client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")

user_router = APIRouter()

@user_router.get("/users/{email}")
async def get_user(email: str):
    user = users.find_one({"email": email})
    if user:
        return individual_serial(user)
    raise HTTPException(status_code=404, detail="User not found")

@user_router.post("/users")
async def create_user(user: User):
    existing_user = users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    user_dict = user.dict()
    result = users.insert_one(user_dict)
    new_user = users.find_one({"_id": result.inserted_id})
    return individual_serial(new_user)


@user_router.post("/userinfo")
async def get_userinfo(request: Request):
    data = await request.json()
    code = data.get("code")

    token_payload = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }

    async with httpx.AsyncClient() as client:
        token_res = await client.post(GOOGLE_TOKEN_URL, data=token_payload)
        token_data = token_res.json()

        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token") 

        if not access_token:
            return {"error": "Token exchange failed", "details": token_data}

        # Get user's email
        profile_res = await client.get(
            f"{GMAIL_API_BASE}/users/me/profile",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        email = profile_res.json().get("emailAddress")

        # Get user's name
        userinfo_res = await client.get(
            USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        name = userinfo_res.json().get("name")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token, 
            "email": email,
            "name": name,
        }