from bson import ObjectId

def individual_serial(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user.get("name"),
        "email": user.get("email"),
        "access_token": user.get("access_token"),
        "refresh_token": user.get("refresh_token"),
        "processed_email_ids": user.get("processed_email_ids", [])
    }

def list_serial(users) -> list:
    return [individual_serial(user) for user in users]
