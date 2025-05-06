import streamlit as st

def hide_sidebar():
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def show_sidebar():
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            display: block;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Define any additional styles needed for your app
STYLES = {
    "auth_page_style": """
        <style>
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #000000 30%, #2e2e70 100%);
            background-size: cover;
        }
        [data-testid="stHeader"] {
            background-color: rgba(0, 0, 0, 0) !important;
        }
        .stButton > button {
            background-color: #6A5ACD;
            color: white;
            padding: 15px;
            border-radius: 10px;
            border: none;
            cursor: pointer;
            margin-top: 10px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        </style>
    """
}