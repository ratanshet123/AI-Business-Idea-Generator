import firebase_admin
from firebase_admin import credentials, auth, firestore

# ✅ Check if Firebase is already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(r"D:\Major project\database\firebase-adminsdk.json")
    firebase_admin.initialize_app(cred)

# ✅ Initialize Firestore database
db = firestore.client()

def sign_up(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        
        # ✅ Save user info to Firestore
        user_ref = db.collection("users").document(user.uid)
        user_ref.set({"email": email})

        return f"User {email} created successfully!"
    except Exception as e:
        return f"Error: {str(e)}"
    
def sign_in(email, password):
    try:
        user = auth.get_user_by_email(email)
        
        # ❌ This does NOT authenticate the password! 
        # Firebase Admin SDK cannot verify passwords.
        return f"User {email} exists! Use Firebase Client SDK for login."
    
    except Exception as e:
        return f"Error: {str(e)}"
