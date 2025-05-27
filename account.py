import streamlit as st
from firebase_config import get_user_data
from streamlit_extras.stylable_container import stylable_container
import os
import time

# Define the STYLES dictionary that was missing
STYLES = {
    "card_style": """
    {
        background-color: #212147;
        border-radius: 10px;
        padding: 20px;
        min-height: 60px;
        margin-bottom: 20px;
    }
    """,
    "p_style": """
    {
        background-color: #18183E;
        border-radius: 10px;
        padding: 20px;
        min-height: 60px;
        margin-bottom: 20px;
    }
    """
}

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
    
    /* Logout button style */
    .stButton > button {
        background-color: #e74c3c;
        color: white;
        padding: 8px 16px;
        border-radius: 5px;
        border: none;
        cursor: pointer;
        font-weight: bold;
    }
    
    /* Profile field style */
    .profile-field {

    }
    
    /* Field label style */
    .field-label {
        color: #cccccc;
        font-size: 14px;
        margin-bottom: 5px;
    }
    
    /* Profile container */
    .profile-container {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    /* Profile card */
    .profile-card {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    
    /* Avatar image */
    .avatar-image {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        border: 3px solid rgba(255, 255, 255, 0.3);
        margin: 0 auto 15px auto;
        display: block;
    }
    
    /* Profile name */
    .profile-name {
        color: white;
        font-size: 24px;
        margin-bottom: 5px;
    }
    
    /* Profile email */
    .profile-email {
        color: #cccccc;
        font-size: 16px;
    }
    
    </style>
    """, unsafe_allow_html=True)

def account_page():
    add_custom_css()
    
    user = st.session_state.get("user", {})
    
    if not user or 'localId' not in user:
        st.error("User not logged in or session expired.")
        if st.button("Go to Login"):
            st.session_state["selected_page"] = "Login"
            st.rerun()
        return
    
    # Get user data using the stored token if available
    id_token = user.get('idToken')
    user_id = user.get('localId')
    

    
    # Try to get user data from Firebase
    user_data = get_user_data(user_id, id_token)
    
    if user_data is None:
        st.warning("Unable to retrieve user data from Firebase. Using session data as fallback.")
        # Fall back to session state data if database retrieval fails
        user_data = {
            'name': user.get('name', 'Not Provided'),
            'email': user.get('email', 'Not Provided'),
            'first_name': user.get('first_name', ''),
            'last_name': user.get('last_name', ''),
            'phone': user.get('phone', 'Not Provided'),
            'college': user.get('college', 'Not Provided'),
            'address': user.get('address', 'Not Provided'),
        }

    
    st.title("Account Profile")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Using Streamlit's native components for profile image and info
        with stylable_container(key="img", css_styles=STYLES["p_style"]):
        
        # Use initials avatar service
            initials = f"{user_data.get('first_name', '')[:1]}{user_data.get('last_name', '')[:1]}"
            avatar_url = f"https://ui-avatars.com/api/?name={user_data.get('first_name', '')}+{user_data.get('last_name', '')}&background=random&color=fff&size=150"
            st.markdown(f'<img src="{avatar_url}" class="avatar-image">', unsafe_allow_html=True)
        
        # Display name and email
            st.markdown(f'<h3 class="profile-name">{user_data.get("first_name", "")} {user_data.get("last_name", "")}</h3>', unsafe_allow_html=True)
            st.markdown(f'<p class="profile-email">{user_data.get("email", "")}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
            if st.button("Logout"):
                st.session_state.clear()
                st.success("You have been logged out.")
                st.session_state["selected_page"] = "Home"
                st.rerun()
    
    with col2:
        col3, col4 = st.columns(2, gap='medium')
        # Using native Streamlit components for user details
        with col3:
            with stylable_container(key="first_name_container", css_styles=STYLES["card_style"]):   
               st.markdown('<p class="field-label">First Name</p>', unsafe_allow_html=True) 
               st.markdown(f'<div class="profile-field">{user_data.get("first_name", "Not Provided")}</div>', unsafe_allow_html=True)
                      
            with stylable_container(key="phone_container", css_styles=STYLES["card_style"]):   
                st.markdown('<p class="field-label">Phone</p>', unsafe_allow_html=True)
                st.markdown(f'<div class="profile-field">{user_data.get("phone", "Not Provided")}</div>', unsafe_allow_html=True)
            
            with stylable_container(key="college_container", css_styles=STYLES["card_style"]): 
                st.markdown('<p class="field-label">College</p>', unsafe_allow_html=True)
                st.markdown(f'<div class="profile-field">{user_data.get("college", "Not Provided")}</div>', unsafe_allow_html=True)
        
        with col4:
            with stylable_container(key="last_name_container", css_styles=STYLES["card_style"]):   
                st.markdown('<p class="field-label">Last Name</p>', unsafe_allow_html=True)
                st.markdown(f'<div class="profile-field">{user_data.get("last_name", "Not Provided")}</div>', unsafe_allow_html=True)
                
            with stylable_container(key="email_container", css_styles=STYLES["card_style"]): 
                st.markdown('<p class="field-label">Email</p>', unsafe_allow_html=True)
                st.markdown(f'<div class="profile-field">{user_data.get("email", "Not Provided")}</div>', unsafe_allow_html=True)
        
        # Add address field in a row spanning both columns
            with stylable_container(key="address_container", css_styles=STYLES["card_style"]): 
                st.markdown('<p class="field-label">Address</p>', unsafe_allow_html=True)
                st.markdown(f'<div class="profile-field">{user_data.get("address", "Not Provided")}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    account_page()