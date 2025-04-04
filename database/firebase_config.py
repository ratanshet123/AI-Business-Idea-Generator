import firebase_admin
from firebase_admin import credentials, firestore

# ✅ Initialize Firebase only if not already initialized
if not firebase_admin._apps:
    CREDENTIALS_PATH = r"D:\Major project\database\firebase-adminsdk.json"
    cred = credentials.Certificate(CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)

# ✅ Initialize Firestore database
db = firestore.client()
