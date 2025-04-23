from pymongo import MongoClient

client = MongoClient("mongodb+srv://manvithreddem:manvithreddem@gmailaiapp.kmwfq2d.mongodb.net/?retryWrites=true&w=majority&appName=GmailAIapp")

db = client.backend

users = db["users"]