import streamlit as st
import requests
from PIL import Image
from streamlit_extras.stylable_container import stylable_container

# Define the style for background container
STYLES = {
    "form_style": """
    {
        background-color:#9CAEEF;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 30px;
    }
    """
}

def contact():
    st.title("Contact Us")

    # Apply background style to SheetDB form using stylable container
    with stylable_container(key="sheetdb_form", css_styles=STYLES["form_style"]):
        st.components.v1.html("""
            <div style="margin: 20px 0;">
                <script src="https://sheetdb.io/s/f/i0t89k3ew8b6q.js"></script>
            </div>
        """, height=400)

    # Developer Cards Section
    st.subheader("Meet Our Team")
    col1, col2, col3 = st.columns(3, gap='medium')
    
    with col1:
        with st.container(border=True):        
            st.image("image/om.png")
            st.write("Om Wanjari")
    with col2:
        with st.container(border=True):
            st.image("image/vedant.png")
            st.write("Vedant Birewar")
    with col3:
        with st.container(border=True):
            st.image("image/shreya.png")
            st.write("Shreya Yadawar")
    
    col1, col2, col3 = st.columns(3, gap='medium')
    
    with col1:
        with st.container(border=True):
            st.image("image/shivam.png")
            st.write("Shivam Durbule")
    with col2:
        with st.container(border=True):
            st.image("image/vivek.png")
            st.write("Vivek Togarwar")
    with col3:
        st.title("")  # Placeholder if needed

if __name__ == "__main__":
    contact()
