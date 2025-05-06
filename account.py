import streamlit as st
from firebase_config import get_user_data

def account_page():
    user = st.session_state.get("user", {})

    if not user or 'localId' not in user:
        st.error("User not logged in or session expired.")
        return

    user_data = get_user_data(user.get('localId', ''))

    if user_data is None:
        st.warning("No additional user data found. Using default values.")
        user_data = {}  # Use an empty dictionary to avoid NoneType issues

    st.title("Account Page")

    with st.container(border=True):
        st.write(f":grey[Name] : {user_data.get('name', 'Not Provided')}")
        st.write(f":grey[Email] : {user_data.get('email', user.get('email', 'Not Provided'))}")

    if st.button("Logout"):
        st.session_state.clear()
        st.success("You have been logged out.")
        st.session_state["selected_page"] = "Home"
        st.rerun()

if __name__ == "__main__":
    account_page()
