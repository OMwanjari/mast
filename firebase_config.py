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

def save_user_data(user_id, name, email):
    user_token = auth_pyrebase.current_user.get('idToken') if auth_pyrebase.current_user else None
    if user_token:
        database.child("users").child(user_id).set({
            "name": name,
            "email": email
        }, user_token)
    else:
        print("Error: No valid authentication token found. User may not be logged in.")

def get_user_data(user_id):
    user_token = auth_pyrebase.current_user.get('idToken') if auth_pyrebase.current_user else None
    if user_token:
        return database.child("users").child(user_id).get(user_token).val()
    else:
        print("Error: No valid authentication token found. User may not be logged in.")
        return None
