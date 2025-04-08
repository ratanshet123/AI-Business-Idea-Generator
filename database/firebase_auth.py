import requests
import json
import firebase_admin
from firebase_admin import credentials, auth, firestore

# ✅ Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(r"D:\Major project\database\firebase-adminsdk.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 🔐 Get this from Firebase Console > Project Settings > Web API Key
FIREBASE_WEB_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

def sign_up(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        db.collection("users").document(user.uid).set({"email": email})
        return f"✅ User {email} created successfully!"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def sign_in(email, password):
    """Authenticate user via Firebase REST API (password check)"""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    response = requests.post(url, data=json.dumps(payload))
    data = response.json()

    if "idToken" in data:
        return {
            "status": "success",
            "idToken": data["idToken"],
            "email": data["email"],
            "localId": data["localId"]
        }
    else:
        return {
            "status": "error",
            "message": data.get("error", {}).get("message", "Unknown error")
        }
