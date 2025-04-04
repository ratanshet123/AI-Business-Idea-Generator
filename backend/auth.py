from firebase_admin import auth

def sign_up(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        return f"User {email} created successfully!"
    except Exception as e:
        return str(e)

def sign_in(email, password):
    # Firebase Admin SDK does not handle sign-in, use Firebase Client SDK in frontend
    return "Sign-in should be handled in frontend using Firebase Auth."
