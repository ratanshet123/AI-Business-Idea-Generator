from database.firebase_config import db
from firebase_admin import firestore  # ✅ Import Firestore module

def save_business_idea(user_email, idea):
    """
    Save a business idea in Firestore under the user's document.
    """
    doc_ref = db.collection("business_ideas").document(user_email)
    doc_ref.set({"ideas": firestore.ArrayUnion([idea])}, merge=True)
    return "Idea saved successfully!"

def get_saved_ideas(user_email):
    """
    Retrieve saved business ideas for a user.
    """
    doc_ref = db.collection("business_ideas").document(user_email)
    doc = doc_ref.get()
    return doc.to_dict().get("ideas", []) if doc.exists else []
