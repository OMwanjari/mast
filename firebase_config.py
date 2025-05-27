import firebase_admin
from firebase_admin import credentials, auth, db
import pyrebase

# Initialize the Firebase Admin SDK with the service account key
cred = credentials.Certificate("serviceAccountKey.json")
# Check if Firebase Admin is already initialized
try:
    firebase_app = firebase_admin.get_app()
except ValueError:
    firebase_app = firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://afit-15355-default-rtdb.firebaseio.com'
    })

# Pyrebase configuration (for user sign-in and sign-up)
firebase_config = {
    "apiKey": "AIzaSyCzWLxei08ODPFqXddH1kisF8DqcdLZPQE",
    "authDomain": "afit-15355.firebaseapp.com",
    "databaseURL": "https://afit-15355-default-rtdb.firebaseio.com",
    "projectId": "afit-15355",
    "storageBucket": "afit-15355.appspot.com",
    "messagingSenderId": "737169749315",
    "appId": "1:737169749315:web:bdc13ece735ba831782bf6",
    "measurementId": "G-1H8HK7ZXKD",
}

firebase = pyrebase.initialize_app(firebase_config)
auth_pyrebase = firebase.auth()
database = firebase.database()

def save_user_data(user_id, name, email, id_token=None, phone=None, first_name=None, last_name=None, college=None, address=None):
    """
    Save user data to Firebase Realtime Database.
    If id_token is provided, it will use that token.
    If not, it will try to use the current user's token if available.
    
    Extended to support additional user fields.
    """
    try:
        # Prepare user data with all fields
        user_data = {
            "name": name,
            "email": email
        }
        
        # Add optional fields if provided
        if phone:
            user_data["phone"] = phone
        if first_name:
            user_data["first_name"] = first_name
        if last_name:
            user_data["last_name"] = last_name
        if college:
            user_data["college"] = college
        if address:
            user_data["address"] = address
            
        # If token is provided directly, use it
        if id_token:
            database.child("users").child(user_id).set(user_data, id_token)
            return True
        # Otherwise try to use current user's token
        elif hasattr(auth_pyrebase, 'current_user') and auth_pyrebase.current_user:
            user_token = auth_pyrebase.current_user.get('idToken')
            if user_token:
                database.child("users").child(user_id).set(user_data, user_token)
                return True
        # If no token is available, use admin SDK
        else:
            # Use Firebase Admin SDK instead
            ref = db.reference(f"/users/{user_id}")
            ref.set(user_data)
            return True
    except Exception as e:
        print(f"Error saving user data: {str(e)}")
        return False

def get_user_data(user_id, id_token=None):
    """
    Get user data from Firebase Realtime Database.
    If id_token is provided, it will use that token.
    If not, it will try to use the current user's token if available.
    """
    try:
        # If token is provided directly, use it
        if id_token:
            return database.child("users").child(user_id).get(id_token).val()
        # Otherwise try to use current user's token
        elif hasattr(auth_pyrebase, 'current_user') and auth_pyrebase.current_user:
            user_token = auth_pyrebase.current_user.get('idToken')
            if user_token:
                return database.child("users").child(user_id).get(user_token).val()
        # If no token is available, use admin SDK
        else:
            # Use Firebase Admin SDK instead
            ref = db.reference(f"/users/{user_id}")
            return ref.get()
    except Exception as e:
        print(f"Error getting user data: {str(e)}")
        return None

def update_user_data(user_id, data, id_token=None):
    """
    Update user data in Firebase Realtime Database.
    If id_token is provided, it will use that token.
    If not, it will try to use the current user's token if available.
    
    data: dictionary of fields to update
    """
    try:
        # If token is provided directly, use it
        if id_token:
            database.child("users").child(user_id).update(data, id_token)
            return True
        # Otherwise try to use current user's token
        elif hasattr(auth_pyrebase, 'current_user') and auth_pyrebase.current_user:
            user_token = auth_pyrebase.current_user.get('idToken')
            if user_token:
                database.child("users").child(user_id).update(data, user_token)
                return True
        # If no token is available, use admin SDK
        else:
            # Use Firebase Admin SDK instead
            ref = db.reference(f"/users/{user_id}")
            ref.update(data)
            return True
    except Exception as e:
        print(f"Error updating user data: {str(e)}")
        return False