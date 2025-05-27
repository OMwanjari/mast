import streamlit as st
import json
from firebase_config import auth_pyrebase, save_user_data, database

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
    
    /* Signup button style */
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
    .stTextInput input, .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
        border-radius: 5px;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Helper function to create a new user
def create_new_user(email, password, first_name, last_name, phone, college, address):
    try:
        # Input validation before Firebase call
        if len(first_name.strip()) < 2 or len(last_name.strip()) < 2:
            st.error("First and Last name must be at least 2 characters long.")
            return None
        if len(password) < 6:
            st.error("Password must be at least 6 characters long.")
            return None
        if not phone.strip():
            st.error("Phone number is required.")
            return None
        if not college.strip():
            st.error("College name is required.")
            return None
        if not address.strip():
            st.error("Address is required.")
            return None
            
        # Create user using Firebase authentication
        user = auth_pyrebase.create_user_with_email_and_password(email, password)
        
        # Sign in to get the id token
        user_auth = auth_pyrebase.sign_in_with_email_and_password(email, password)
        id_token = user_auth['idToken']
        
        # Create full name from first and last name
        full_name = f"{first_name} {last_name}"
        
        # Save user data to the database with the token
        success = save_user_data(
            user_id=user['localId'],
            name=full_name,
            email=email,
            id_token=id_token,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            college=college,
            address=address
        )
        
        if not success:
            st.error("Account created but failed to save user data. Please try logging in.")
            
        return user_auth  # Return the signed-in user with token
        
    except Exception as e:
        # Try to parse the error as JSON (Firebase error format)
        try:
            error_str = str(e)
            # Extract JSON portion from the error message
            if '{' in error_str:
                json_str = error_str[error_str.index('{'):]
                error_data = json.loads(json_str)
                error_message = error_data.get('error', {}).get('message', '').lower()
                
                if "email_exists" in error_message:
                    st.error("This email is already registered. Please log in or use a different email.")
                elif "weak_password" in error_message:
                    st.error("Password is too weak. Use at least 6 characters with a mix of letters and numbers.")
                elif "invalid_email" in error_message:
                    st.error("Invalid email format. Please enter a valid email address.")
                elif "too_many_requests" in error_message:
                    st.error("Too many attempts. Please wait a few minutes and try again.")
                else:
                    st.error(f"Signup failed: {error_message}. Please try again or contact support.")
            else:
                st.error(f"Signup failed: {error_str}. Please try again or contact support.")
        except json.JSONDecodeError:
            # If JSON parsing fails, fall back to raw error message
            st.error(f"Signup failed: {str(e)}. Please try again or contact support.")
        return None

# Function to manage the signup page
def signup_page():
    add_custom_css()
    
    col1, col2 = st.columns([1, 1], gap='medium', vertical_alignment="center")

    with col1:
        st.image("signin.png")
    
    with col2:
        st.title("Sign Up")

        first_name = st.text_input("First Name", placeholder="Enter your first name")
        last_name = st.text_input("Last Name", placeholder="Enter your last name")
        email = st.text_input("Email", placeholder="Enter your email")
        phone = st.text_input("Phone", placeholder="Enter your phone number")
        college = st.text_input("College", placeholder="Enter your college name")
        address = st.text_area("Address", placeholder="Enter your address")
        password = st.text_input("Password", placeholder="Enter your password", type="password")

        if st.button("Sign Up"):
            # Initial client-side validation
            if not all([first_name.strip(), last_name.strip(), email.strip(), phone.strip(), college.strip(), address.strip(), password.strip()]):
                st.error("All fields (First Name, Last Name, Email, Phone, College, Address, Password) are required.")
            else:
                with st.spinner("Creating account..."):
                    user = create_new_user(email, password, first_name, last_name, phone, college, address)
                    if user:
                        try:
                            st.success("Account created successfully!")
                            # Create full name from first and last name
                            full_name = f"{first_name} {last_name}"
                            st.session_state["user"] = {
                                "localId": user['localId'],
                                "email": email,
                                "name": full_name,
                                "first_name": first_name,
                                "last_name": last_name,
                                "phone": phone,
                                "college": college,
                                "address": address,
                                "idToken": user['idToken']  # Store the token in session state
                            }
                            st.session_state["selected_page"] = "Student"
                            st.rerun()
                        except Exception as session_error:
                            st.error(f"Account created but failed to initialize session: {str(session_error)}")

        # Redirect to login
        col1, col2 = st.columns(2)
        with col1:
            st.write("Already have account?")
        with col2:
            if st.button("Login here", key="login_link"):
                st.session_state["selected_page"] = "Login"
                st.rerun()

# Run the app
if __name__ == "__main__":
    signup_page()