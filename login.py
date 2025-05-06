import streamlit as st
from firebase_config import auth_pyrebase, get_user_data
# Helper function to add custom CSS styles
def add_custom_css():
    st.markdown("""
    <style>
    /* Background gradient */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #000000 30%, #2e2e70 100%);
        background-size: cover;
    }
    
    /* Remove header background */
    [data-testid="stHeader"] {
        background-color: rgba(0, 0, 0, 0) !important;
    }
    
    /* Login button style */
    .stButton > button {
        background-color: #7857FF;
        color: white;
        padding: 5px;
        border-radius: 5px;
        border: none;
        cursor: pointer;
        width: 100%;
        margin-top: 5px;
    }
    
    /* Input field styles */
    .stTextInput input {
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
        border-radius: 5px;
        padding: 10px;
    }
    
    /* Signup text container */
    .signup-container {
        display: flex;
        align-items: center;
        gap: 5px;
        margin-top: 20px;
        justify-content: center;
    }
    
    .signup-text {
        color: #ffffff;
        margin: 0;
    }
    
    .signup-link {
        color: #7857FF;
        text-decoration: none;
        cursor: pointer;
        background: none;
        border: none;
        padding: 0;
        font: inherit;
    }
    
    .signup-link:hover {
        text-decoration: underline;
    }
    </style>
    """, unsafe_allow_html=True)
# Helper function to authenticate the user
def authenticate_user(email, password):
    try:
        # Attempt to sign in user with Firebase
        user = auth_pyrebase.sign_in_with_email_and_password(email, password)
        
        # If authentication successful, get user data
        user_data = get_user_data(user['localId'])
        if not user_data:
            st.warning("No additional user data found. Using default values.")
            user_data = {"name": "Unknown"}
        return user, user_data
        
    except Exception as e:
        error_str = str(e)
        
        # Handle Firebase specific error messages
        if "INVALID_PASSWORD" in error_str:
            st.error("Invalid password. Please try again.")
        elif "INVALID_EMAIL" in error_str:
            st.error("Invalid email format. Please enter a valid email.")
        elif "EMAIL_NOT_FOUND" in error_str:
            st.error("No account found with this email. Please sign up first.")
        elif "TOO_MANY_ATTEMPTS_TRY_LATER" in error_str:
            st.error("Too many failed attempts. Please try again later.")
        elif "INVALID_LOGIN_CREDENTIALS" in error_str:
            st.error("Invalid login credentials. Please check your email and password.")
        else:
            # Log the full error for debugging
            print(f"Firebase Auth Error: {error_str}")
            st.error("An error occurred during login. Please try again.")
        
        return None, None

def login_page():
    add_custom_css()
    
    col1, col2 = st.columns([1, 1], gap='medium')
    with col1:
        st.image("login.png")
    with col2:
        st.title("Login")
        
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", placeholder="Enter your password", type="password")
        
        if st.button("Login"):
            if not email or not password:
                st.error("Both email and password are required.")
            else:
                # Add loading state while authenticating
                with st.spinner("Logging in..."):
                    user, user_data = authenticate_user(email, password)
                    
                    if user:
                        st.success(f"Welcome back, {user_data.get('name', 'User')}!")
                        st.session_state["user"] = {
                            "localId": user['localId'],
                            "email": email,
                            "name": user_data.get('name', 'Not Provided')
                        }
                        st.session_state["selected_page"] = "Student"
                        st.rerun()
        col1, col2 = st.columns(2, gap="small")
        with col1:
            st.markdown('<p class="signup-text">Don\'t have an account?</p>', unsafe_allow_html=True)
        with col2:
            if st.button("Sign up here", key="signup_link"):
                st.session_state["selected_page"] = "Signup"
                st.rerun()
                
# Run the app
if __name__ == "__main__":
    login_page()

