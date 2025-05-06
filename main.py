import streamlit as st
from dotenv import load_dotenv
from streamlit_option_menu import option_menu
import base64
from styles import hide_sidebar, show_sidebar, STYLES

# Set page config as the VERY FIRST Streamlit command
st.set_page_config(layout="wide")

# Load environment variables
load_dotenv()

def get_svg_base64(svg_path):
    with open(svg_path, "rb") as svg_file:
        svg_data = svg_file.read()
    return base64.b64encode(svg_data).decode()

def main():
    # Import modules here to avoid executing Streamlit commands during import
    from login import login_page
    from signup import signup_page
    from account import account_page
    from home import home
    from student import student_function
    from admin import admin_function
    from contact import contact

    # Initialize session state
    if 'selected_page' not in st.session_state:
        st.session_state.selected_page = "Home"
    if 'user' not in st.session_state:
        st.session_state.user = None

    # Authentication page routing
    if st.session_state.selected_page in ["Login", "Signup"]:
        hide_sidebar()
        st.markdown(STYLES["auth_page_style"], unsafe_allow_html=True)
        if st.session_state.selected_page == "Login":
            login_page()
        else:
            signup_page()
        return

    # Show sidebar for other pages
    show_sidebar()

    with st.sidebar:
        # Sidebar content like logo, menu, etc.
        svg_base64 = get_svg_base64("logo.svg")
        st.markdown(
            f"""
            <div style="text-align: center;">
                <img src="data:image/svg+xml;base64,{svg_base64}" width="50">
            </div>
            """,
            unsafe_allow_html=True
        )

        selected = option_menu(
            menu_title="",
            options=["Home", "Student", "Admin", "Contact", "Account"],
            icons=["house", "backpack", "file-person", "telephone", "person-circle"],
            menu_icon="",
            default_index=["Home", "Student", "Admin", "Contact", "Account"].index(st.session_state.selected_page)
        )

        if selected != st.session_state.selected_page:
            st.session_state.selected_page = selected
            st.rerun()

    # Page routing
    page_functions = {
        "Home": home,
        "Student": student_function,
        "Admin": admin_function,
        "Contact": contact,
        "Account": account_page
    }

    if st.session_state.selected_page in ["Home", "Contact"]:
        page_functions[st.session_state.selected_page]()
    else:
        if st.session_state.user is None:
            st.warning("You need to log in to access this page.")
            st.session_state.selected_page = "Login"
            st.rerun()
        else:
            page_functions[st.session_state.selected_page]()

if __name__ == "__main__":
    main()