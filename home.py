import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import os

# Constants
TEMPLATE_PATH = r"STT.docx"
IMAGE_PATH = r"ats.png"

# Styles
STYLES = {
    "page_bg_img": """
    <style>
    [data-testid="stAppViewContainer"] {
      background: linear-gradient(135deg, #000000 30%, #2e2e70 100%);
      background-size: cover;
    }
    [data-testid="stHeader"] {
      background-color: rgba(0, 0, 0, 0) !important;
    }
    .student-heading {
        font-size: 48px;
        font-weight: bold;
        margin-bottom: 30px;
        color: white;
    }
    .nav-button {
        background-color: #6A5ACD;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        text-decoration: none;
        display: inline-block;
        margin-top: 20px;
    }
    .stButton > button {
        height: 30px;
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
    }
    .stButton > button i {
        margin-right: 10px;
    }
    </style>
    """,
    "card_style": """
    {
        background-color: #1a1a40;
        border-radius: 10px;
        padding: 20px;
        min-height: 50px;
        margin-bottom: 20px;
    }
    """
}

def load_docx_file(file_path):
    try:
        with open(file_path, "rb") as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"Template file not found at {file_path}")
        return None

def navigation_button(label, page, unique_id):
    if st.button(label, key=f"{page.lower()}_{unique_id}_nav"):
        st.session_state.selected_page = page
        st.rerun()

def home():
    st.markdown(STYLES["page_bg_img"], unsafe_allow_html=True)

    with st.container(border=True):
        col1, col2 = st.columns([1.5, 1])
        with col1:
            st.title("Is your resume good enough for compitative market?")
            st.write(":grey[AFIT leveraging technologies such as NLP and LLMs, Unlock Student Potential with AI-Powered Career Insights]")
            st.subheader("")
            navigation_button("🚀 Get Started for free", "Student", "header")
        with col2:
            st.image(IMAGE_PATH, use_container_width=True)

    with stylable_container(key="resume_download", css_styles=STYLES["card_style"]):
        st.markdown("""
            <h3>
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 10px;">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                </svg>
                Download Our Professional Resume Template
            </h3>
        """, unsafe_allow_html=True)
        st.caption("Get a head start with our professionally designed template!")
        
        docx_file = load_docx_file(TEMPLATE_PATH)
        if docx_file is not None:
            st.download_button(
                label="⬇️ Download Template",
                data=docx_file,
                file_name="Professional_Resume_Template.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
    st.title("")
    st.subheader("Interactive dashboards to track student progress")
    st.write(":grey[We visualize the data for proper analysis of data and find meaning in it]")
    st.caption("")
    st.image(r"dash.png")
    
    st.title("")
    st.subheader("Key Features")
    col1,col2,col3= st.columns([1.4,1,1],gap='medium',border=True)
    with col1:
        st.image(r"image\resume_analysis.png")
        st.write("Resume Analysis with ATS Scoring")
        st.caption("Evaluate resumes with AI-driven ATS scoring (1-100) to ensure industry readiness.")
    with col2:
        st.image(r"image\skill_gap.png")
        st.write("Skill Gap Identification")
        st.caption("Identify skill gaps and recommend actionable steps to bridge them effectively.")
    with col3:
        st.image(r"image\course.png")
        st.write("AI-Powered Course Recommendations")
        st.caption("Get personalized course suggestions tailored to industry demands and student profiles.")
    
    col1,col2,col3= st.columns([1,1,1.4],gap='medium',border=True)
    with col1:
        st.image(r"image\data_visual.png")
        st.write("Data Visualization Dashboard")
        st.caption("Track student progress and institutional performance with interactive dashboards.")
    with col2:
        st.image(r"image\bulk.png")
        st.write("Bulk Resume Processing")
        st.caption("Efficiently analyze multiple resumes for administrators and career counselors")
    with col3:
        st.image(r"image\job_desc.png")
        st.write("Job Description Matching")
        st.caption("Match student profiles with relevant job descriptions for better placement outcomes.") 

def student_page():
    st.title("Student Page")
    st.write("This is the student page. Add your content here.")
    navigation_button("🏠 Back to Home", "Home", "student")

def admin_page():
    st.title("Admin Page")
    st.write("This is the admin page. Add your content here.")
    navigation_button("🏠 Back to Home", "Home", "admin")

def main():
    if 'selected_page' not in st.session_state:
        st.session_state.selected_page = "Home"

    page_functions = {
        "Home": home,
        "Student": student_page,
        "Admin": admin_page
    }

    page_functions[st.session_state.selected_page]()

if __name__ == "__main__":
    main()