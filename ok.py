import streamlit as st

st.image("ats.png", width=150)  # Replace with your image path
if st.link_button("Click me", "https://example.com"):
    st.success("Button clicked!")
