import streamlit as st
import google.generativeai as genai
import plotly.graph_objects as go
from utils import process_single_pdf, extract_score_and_feedback

# Configure generative AI with API key
genai.configure(api_key='AIzaSyBDGiMgAEF4zEX-w9nkS-cl3DSFFrFm2DA')

STYLES = """
<style> 
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #000000 30%, #2e2e70 100%);
    background-size: cover;
    color: #ffffff;
}
[data-testid="stHeader"] {
    background-color: rgba(0, 0, 0, 0) !important;
}
.student-heading {
    font-size: 42px;
    font-weight: 700;
    background: linear-gradient(120deg, #4f46e5, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin: 2rem 0;
    padding: 1rem;
}
.subheading {
    color: #a5b4fc;
    font-size: 18px;
    text-align: center;
    margin-bottom: 2rem;
}
.stButton > button {
    height: 48px;
    width: 100%;
    background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 600;
    transition: transform 0.2s;
    margin: 8px 0;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
}
.file-uploader {
    background-color: rgba(30, 41, 59, 0.7);
    padding: 24px;
    border-radius: 12px;
    border: 1px solid #3f3f6f;
}
.text-area, .result-box {
    background-color: rgba(30, 41, 59, 0.7);
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #3f3f6f;
    margin: 16px 0;
}
.result-box {
    background-color: rgba(37, 41, 69, 0.7);
    line-height: 1.6;
}
.score-container {
    background: rgba(30, 41, 59, 0.7);
    padding: 16px;
    border-radius: 12px;
    margin: 16px 0;
    border: 1px solid #3f3f6f;
    display: flex;
    flex-direction: column;
    align-items: center;
}
div[data-testid="stMarkdownContainer"] > p {
    color: #e2e8f0;
}
.analysis-header {
    color: #a5b4fc;
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 16px;
    text-align: center;
}
.score-label {
    color: #a5b4fc;
    font-size: 18px;
    margin-top: 8px;
    text-align: center;
}
</style>
"""
def extract_score_and_feedback(response_text):
    """
    Extract score and feedback from AI response.
    Returns a tuple of (score, feedback_text)
    """
    try:
        if "SCORE:" in response_text:
            score_part = response_text.split("SCORE:")[1].strip()
            score_str = ""
            for char in score_part:
                if char.isdigit() or char == '.':
                    score_str += char
                else:
                    break
            
            score = int(float(score_str))
            
            if "ANALYSIS:" in response_text:
                feedback = response_text.split("ANALYSIS:")[1].strip()
            else:
                feedback = response_text.replace(f"SCORE: {score_str}", "").strip()
            
            return score, feedback
    except Exception as e:
        # If extraction fails, return a default score and the full response
        return 0, response_text
    
    import re
    score_matches = re.findall(r'\b\d{1,3}\b', response_text)
    if score_matches:
        for match in score_matches:
            score = int(match)
            if 0 <= score <= 100:
                return score, response_text
    
    return 0, response_text

def generate_ai_response(prompt):
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred: {str(e)}"

def create_progress_indicator(score, key_prefix):
    try:
        score = int(score)
        if score < 0:
            score = 0
        elif score > 100:
            score = 100
    except (ValueError, TypeError):
        score = 0  # Default to 0 if conversion fails
        
    color = "#ef4444" if score < 70 else "#eab308" if score < 85 else "#22c55e"
    
    fig = go.Figure()
    fig.add_trace(go.Pie(
        values=[score, 100-score],
        hole=0.75,
        marker_colors=[color, 'rgba(30, 41, 59, 0.7)'],
        showlegend=False,
        textinfo='none',
        hoverinfo='skip'
        
    ))
    
    fig.update_layout(
        width=200,
        height=200,
        margin=dict(t=20, b=20, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        annotations=[
            dict(
                text=f'{score}%',
                x=0.5,
                y=0.5,
                font_size=28,
                font_color='white',
                showarrow=False
            )
        ]
    )
    
    return fig

PROFILE_MATCH_PROMPT = """
Analyze this resume against the job description using a precise, rule-based approach:
Resume Content:
{resume_content}
Job Description:
{job_description}

Evaluate alignment based solely on the provided content, ignoring ATS optimization or suggestions beyond the job description. Use the following weighted criteria and strict scoring rules:

1. Match Percentage (0-100):
   - Key Skills Alignment (40% weight):
     * Extract skills explicitly listed in the job description as individual items.
     * Extract skills from the resume, treating any mentioned skill (in any section) as valid.
     * Normalize skills: Convert to lowercase, remove extra spaces, and ignore punctuation.
     * Score = (Number of matched skills / Total skills in job description) * 100, capped at 100.
     * Report: "Matched: [number] ([exact comma-separated list of matched skills]), Missing: [number] ([exact comma-separated list of missing skills])".
     * Be precise with the counts - ensure the number of matched skills matches the count of skills in your list, and that the number of missing skills matches the count of skills in your missing list.
   - Experience Relevance (30% weight):
     * Compare professional job titles and years of experience to job description requirements.
     * Score = 100 if all required titles and years match exactly; 0 otherwise (no partial credit).
     * Report: "Matched: [yes/no], Details: [specific matches or mismatches]".
   - Education Fit (20% weight):
     * Match degree level and field to job description.
     * Score = 100 if exact match; 50 if degree level matches but field differs; 0 if neither matches.
     * Report: "Matched: [degree and field], Mismatched: [degree or field]".
   - Overall Presentation (10% weight):
     * Score based on: (1) consistent formatting, (2) readability, (3) relevance.
     * Score = 100 if all 3 perfect; 75 if 2/3; 50 if 1/3; 0 if none.
     * Report: "Strengths: [comma-separated list], Weaknesses: [comma-separated list]".

2. Matching Elements:
   - List exact skills from the job description found in the resume as comma-separated values.
   - List relevant professional experience matches (titles and years).
   - State education alignment (degree and field).

3. Gaps:
   - List skills in the job description missing from the resume as comma-separated values.
   - List experience mismatches (e.g., missing titles, insufficient years).

4. Recommendation:
   - Based on the final score, provide a clear recommendation:
     * If score ≥ 80%: "Ready to Apply: Your profile strongly matches the requirements. Proceed with your application."
     * If score 60-79%: "Consider Improvements: Your profile partially matches the requirements. Make targeted improvements before applying."
     * If score < 60%: "Significant Gaps: There are substantial gaps between your profile and the job requirements. Enhance your resume before applying."
   - Provide actionable next steps:
     * For missing skills: "Click on 'Identify Skill Gaps' to see detailed missing skills."
     * For improvement needs: "Click on 'Get Improvement Plan' for a customized enhancement strategy."

Final Score Calculation:
   - Weighted Score = (Skills Score * 0.4) + (Experience Score * 0.3) + (Education Score * 0.2) + (Presentation Score * 0.1).
   - Round the final score to the nearest whole number.

Format your response as:
SCORE: [final-weighted-score]

MATCH ANALYSIS:
1. Match Percentage:
   - Key Skills Alignment: [score]% (Matched: [number] ([comma-separated list of exactly [number] skills]), Missing: [number] ([comma-separated list of exactly [number] skills]))
   - Experience Relevance: [score]% (Matched: [yes/no], Details: [details])
   - Education Fit: [score]% (Matched: [details], Mismatched: [details])
   - Overall Presentation: [score]% (Strengths: [comma-separated list], Weaknesses: [comma-separated list])
2. Matching Elements:
   - Skills: [comma-separated list]
   - Experience: [comma-separated list]
   - Education: [details]
3. Gaps:
   - Skills: [comma-separated list]
   - Experience: [details]
4. Recommendation:
   - [Recommendation based on score tier]
   - [Actionable next steps with specific button suggestions]

For consistency: Count skills exactly, ensuring the number matches the list. Use exact string matching for skills, normalize text (lowercase, no punctuation), and avoid interpreting synonyms or related terms unless explicitly stated.
"""
ATS_SCORE_PROMPT = """
Perform a comprehensive ATS (Applicant Tracking System) analysis of this resume:
Resume Content:
{resume_content}
Evaluate and score (0-100) based on the following parameters:

1. Impact (20%):
   - Quantifying impact (e.g., metrics, achievements)
   - Use of unique action verbs
   - Avoidance of weak action verbs
   - Correct verb tenses
   - Accomplishment-oriented language

2. Brevity (20%):
   - Appropriate resume length & depth
   - Effective use of bullet points
   - Optimal bullet point length
   - Minimal use of filler words/adverbs
   - Balanced page density

3. Style (20%):
   - Avoidance of buzzwords or clichés
   - Identification of vague buzzwords
   - Correct formatting of dates
   - Presence of essential contact and personal information
   - Readability (font, spacing, structure)
   - Avoidance of personal pronouns

4. Sections (20%):
   - Presence of essential sections (Experience, Education, Skills)
   - Clear and relevant section titles
   - Properly formatted Projects section
   - Well-organized Skills section
   - Absence of unnecessary sections

5. Soft Skills (20%):
   - Demonstration of communication skills
   - Evidence of analytical and problem-solving skills
   - Indication of teamwork abilities
   - Leadership qualities
   - Drive and initiative
Format your response as:
SCORE: [number]
ANALYSIS:
[Provide detailed breakdown of each component with specific recommendations]
"""

MISSING_KEYWORDS_PROMPT = """
Analyze the resume for key skills and qualifications:
Resume Content:
{resume_content}
Job Description:
{job_description}
Provide a detailed analysis in the following format:
1. Missing Critical Elements:
   - Must-have skills not found
   - Required experience gaps
   - Essential qualifications missing
2. Key Skills Present:
   - Technical Skills
   - Soft Skills
   - Domain Expertise
Present the analysis in a clear, structured format .
"""
RESUME_IMPROVEMENT_PROMPT = """
Your task is to analyze the provided resume against the given job description and suggest targeted improvements to increase the candidate's chances of securing an interview.

### **Input Data:**
- **Resume Content:** {resume_content}
- **Job Description:** {job_description}

### **Key Areas of Improvement:**
#### **1. Content Enhancement**
   - Strengthen achievement statements using action verbs and measurable impact.
   - Add quantifiable metrics where applicable to highlight accomplishments.
   - Improve the presentation of technical and domain-specific skills.
   - Optimize the structure and clarity of the professional experience section.

#### **2. ATS (Applicant Tracking System) Optimization**
   - Identify missing or underused keywords relevant to the job description.
   - Improve formatting and section organization for ATS readability.
   - Prioritize content to align with job requirements and industry standards.

#### **3. Course Recommendations for Skill Development**
   - Identify key skills missing in the resume based on the job description.
   - Recommend **real-world courses** with:
     - **Course Name**
     - **Provider (e.g., Coursera, Udemy, LinkedIn Learning, edX, Google, IBM, AWS, Microsoft, etc.)**
     - **Duration (e.g., 4 weeks, 3 months, self-paced)**
   - Suggest certifications that enhance credibility for the desired role.
   - Provide training/resources for both technical and soft skills relevant to the job.

### **Example Course Recommendations Format:**
- **Skill Gap:** Data Analysis with Python  
  - **Course:** *IBM Data Analyst Professional Certificate*  
  - **Provider:** Coursera (IBM)  
  - **Duration:** ~3 months (Self-paced) 
  - **link:** link of course 

- **Skill Gap:** Cloud Computing (AWS)  
  - **Course:** *AWS Certified Solutions Architect – Associate*  
  - **Provider:** Udemy (Amazon AWS)  
  - **Duration:** ~6 weeks  
  - **link:** link of course 

- **Skill Gap:** Leadership & Communication  
  - **Course:** *Developing Executive Presence*  
  - **Provider:** LinkedIn Learning  
  - **Duration:** 4 hours  
  - **link:** link of course 

### **Output Expectations:**
- Provide specific, actionable feedback with clear implementation steps.
- Highlight any gaps between the resume and the job description.
- List real courses from reputable platforms with names, providers, and durations.
- Ensure recommendations are practical, precise, and tailored to the job role.

Focus on optimizing the resume to increase its effectiveness for both recruiters and ATS systems.
"""
def student_function():
    st.markdown(STYLES, unsafe_allow_html=True)
    st.title("Professional Resume Analyzer")    
    st.write(":grey[🔥 Get detailed feedback on your resume to enhance your job application success rate.]")

    if 'counter' not in st.session_state:
        st.session_state.counter = 0
    if 'results' not in st.session_state:
        st.session_state.results = {}
    st.info("Pdf Format only supported")
    with st.container():
        with st.container(border=True):
            uploaded_file = st.file_uploader("📄 Upload your resume in PDF", type=['pdf'], key="resume_upload")
        if uploaded_file == 0:
            st.error("The uploaded file is empty. Please upload a valid PDF.")
            return
        if uploaded_file:
            pdf_content = process_single_pdf(uploaded_file)
            with st.container(border=True):
                job_description = st.text_area("📝 Enter the job description", 
                                             placeholder="Paste the job description here (minimum 50 words)...",
                                             height=200,
                                             key="job_desc")

            col1, col2 = st.columns(2,gap='large')
            col3, col4 = st.columns(2,gap='large')
            results_container = st.container()
            
            with col1:
                    profile_match_clicked = st.button("🎯 Analyze Profile Match", 
                                                    key="profile_match_btn", 
                                                    use_container_width=True)

            with col2:
                    ats_score_clicked = st.button("📊 Calculate ATS Score", 
                                                key="calculate_ats_btn", 
                                                use_container_width=True)

            with col3:
                    keywords_clicked = st.button("🔍 Identify Skill Gaps", 
                                               key="find_keywords_btn", 
                                               use_container_width=True)

            with col4:
                    improvement_clicked = st.button("💡 Get Improvement Plan", 
                                                  key="improvise_resume_btn", 
                                                  use_container_width=True)

            with results_container:
                if profile_match_clicked:
                    if not job_description or len(job_description.split()) < 50:
                        st.warning("⚠️ Please enter at least 50 words in the job description.")
                    else:
                        with st.spinner("🔄 Analyzing profile match..."):
                            response = generate_ai_response(
                                PROFILE_MATCH_PROMPT.format(
                                    resume_content=pdf_content,
                                    job_description=job_description
                                )
                            )
                            score, feedback = extract_score_and_feedback(response)
                            st.session_state.results['profile_match'] = {'score': score, 'feedback': feedback}
                            
                            # Debug info
                            st.write(f"Debug - Score extracted: {score}")
                            
                            with st.container(border=True):
                                fig = create_progress_indicator(score, "profile_match")
                                st.plotly_chart(fig, use_container_width=False)
                                st.markdown("<div class='score-label'>Profile Match Score</div>", unsafe_allow_html=True)
                            
                            with st.container(border=True):
                                st.markdown("<h3 class='analysis-header'>Profile Match Analysis</h3>", unsafe_allow_html=True)
                                st.markdown(feedback, unsafe_allow_html=True)

                elif ats_score_clicked:
                    with st.spinner("🔄 Calculating ATS score..."):
                        response = generate_ai_response(
                            ATS_SCORE_PROMPT.format(
                                resume_content=pdf_content
                            )
                        )
                          
                        score, feedback = extract_score_and_feedback(response)
                        st.session_state.results['ats_score'] = {'score': score, 'feedback': feedback}                        
                        
                        with st.container(border=True):
                            fig = create_progress_indicator(score, "ats")
                            st.plotly_chart(fig, use_container_width=False)
                            st.markdown("<div class='score-label'>ATS Score</div>", unsafe_allow_html=True)
                        
                        with st.container(border=True):
                            st.markdown("<h3 class='analysis-header'>ATS Score Analysis</h3>", unsafe_allow_html=True)
                            st.markdown(feedback, unsafe_allow_html=True)

                elif keywords_clicked:
                    if not job_description or len(job_description.split()) < 50:
                        st.warning("⚠️ Please enter at least 50 words in the job description.")
                    else:
                        with st.spinner("🔄 Analyzing skill gaps..."):
                            response = generate_ai_response(
                                MISSING_KEYWORDS_PROMPT.format(
                                    resume_content=pdf_content,
                                    job_description=job_description
                                )
                            )
                            with st.container(border=True):
                                st.markdown("<h3 class='analysis-header'>Skill Gap Analysis</h3>", unsafe_allow_html=True)
                                st.markdown(response, unsafe_allow_html=True)

                elif improvement_clicked:
                    if not job_description or len(job_description.split()) < 50:
                        st.warning("⚠️ Please enter at least 50 words in the job description.")
                    else:
                        with st.spinner("🔄 Generating improvement plan..."):
                            response = generate_ai_response(
                                RESUME_IMPROVEMENT_PROMPT.format(
                                    resume_content=pdf_content,
                                    job_description=job_description
                                )
                            )
                            with st.container(border=True):
                                st.markdown("<h3 class='analysis-header'>Resume Improvement Plan</h3>", unsafe_allow_html=True)
                                st.markdown(response, unsafe_allow_html=True)

            st.session_state.counter += 1

        else:
            st.info("👆 Please upload your resume to begin the analysis.")

if __name__ == "__main__":
    student_function()