import io
import streamlit as st
import pandas as pd
import pdfplumber
import spacy
from spacy.matcher import Matcher
import re
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import logging

# Suppress Streamlit warnings
logging.getLogger("streamlit").setLevel(logging.ERROR)

# Load spaCy model
def load_nlp_model():
    try:
        return spacy.load("en_core_web_md")
    except OSError:
        st.warning("Downloading spaCy model. This may take a moment...")
        spacy.cli.download("en_core_web_md")
        return spacy.load("en_core_web_md")

nlp = load_nlp_model()

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
    """
}


@st.cache_data(ttl=3600)
@st.cache_resource
def extract_text_from_pdf(file):
    """Extract text from PDF using pdfplumber."""
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

###################################################### Name ##################################################################

def extract_name(doc):
    """Extract name from first line or spaCy entities."""
    first_line = doc.text.strip().split('\n')[0]
    words = first_line.split()
    if 2 <= len(' '.join(words)) <= 30:
        return ' '.join(words)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return "Unknown"

###################################################### Email ##################################################################
def extract_email(text):
    """Extract email using regex."""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(email_pattern, text)
    return match.group(0) if match else None
###################################################### Phone Number #################################################################

def extract_phone_number(text):
    """Extract phone number using regex."""
    phone_pattern = r'\+?\d[\d -]{8,12}\d'
    match = re.search(phone_pattern, text)
    return match.group(0) if match else None

###################################################### Education ##################################################################

def extract_degree(doc):
    """Improved degree extraction using advanced matcher."""
    degree_patterns = {
        'PhD': [
            {"LOWER": {"IN": ["phd", "ph.d", "doctorate"]}},
            {"LOWER": "of", "OP": "?"},
            {"LOWER": "philosophy", "OP": "?"}
        ],
        'Master': [
            {"LOWER": {"IN": ["master", "masters", "m.s", "m.tech", "mba"]}}
        ],
        'Bachelor': [
            {"LOWER": {"IN": ["bachelor", "bachelors", "b.s", "b.tech", "be"]}}
        ]
    }

    matcher = Matcher(nlp.vocab)
    for level, pattern in degree_patterns.items():
        matcher.add(level, [pattern])

    matches = matcher(doc)
    return nlp.vocab.strings[matches[0][0]] if matches else "Bachelor"

###################################################### Department ##################################################################
# Fix 1: Merge duplicate department entries and consolidate keywords
DEPARTMENTS_MAPPING = {
    'Computer Technology': ["ct", "c.tech", "computer technology"],
    'Artificial Intelligence & Data Science': [
        "ai&ds", "aids", "artificial intelligence & data science", 
        "artificial intelligence and data science", "ai and ds", 
        "ai & data science", "data science", "machine learning",
        "artificial intelligence", "data analysis"
    ],
    'Information Technology': ["information technology", "it", "information tech"],
    'Electronics & Telecommunication Engineering': [
        "electronics", "electrical engineering",
        "electronic and telecommunication",
        "electronics and telecommunication",
        "etc", "e&tc", "e & tc", "e and tc"
    ],
    'Computer Science and Engineering': [
        "computer science engineering", "cse",
        "computer science & engineering",
        "computer engineering", "computer science",
        "cs", "cs&e", "cs & e", "cs and e"
    ],
    'Mechanical Engineering': ["mechanical engineering", "me", "mechanical", "mech"],
    'Civil Engineering': ["civil engineering", "ce", "civil"],
    'Electrical Engineering': ["electrical engineering", "ee", "electrical"],
    'Artificial Intelligence & Machine Learning': [
        "aiml", "ai&ml", "ai ml", "ai & ml", "ai and ml"
    ],
    'Industrial Internet of Things': [
        "industrial internet of things",
        "iiot", "industrial iot", "i-iot", "i iot"
    ],
    'Computer Science and Design': [
        "computer science and design",
        "computer design", "cs design", "csd", "cs & design", "cs and design"
    ],
    'Business Administration': [
        "business administration", "mba", "bba", "business management",
        "business studies", "management studies"
    ],
    'Finance': [
        "finance", "financial management", "accounting", "commerce",
        "banking", "investment", "financial analysis"
    ],
    'Human Resources': [
        "human resources", "hr", "personnel management",
        "talent acquisition", "hr management", "hcm"
    ],
    'Operations': [
        "operations", "operations management", "supply chain",
        "logistics", "production management"
    ]
}


# Fix 2: Improved department extraction function
def extract_department(doc, text):
    """Advanced department extraction with more robust matching."""
    text_lower = text.lower()
    
    # Track best match and score
    best_match = None
    best_score = 0
    
    # Direct keyword matching with scoring
    for dept, keywords in DEPARTMENTS_MAPPING.items():
        score = 0
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                # Add points for direct match
                score += 2
            elif keyword in text_lower:  # Partial match
                score += 1
        
        if score > best_score:
            best_score = score
            best_match = dept
    
    # If we found a match with direct keywords, return it
    if best_match and best_score > 0:
        return best_match
            
    # Look for context clues in education sections
    education_sections = []
    education_keywords = ["degree", "graduated", "university", "college", "institute", 
                          "major", "specialization", "bachelor", "master", "b.tech", "m.tech"]
    
    # Find education related sections
    for line in text_lower.split('\n'):
        if any(keyword in line for keyword in education_keywords):
            education_sections.append(line)
    
    # Check department mentions in education sections
    for dept, keywords in DEPARTMENTS_MAPPING.items():
        for section in education_sections:
            if any(keyword in section for keyword in keywords):
                return dept
    
    # Fall back to the most likely department based on technical skills
    tech_skills = extract_skills(doc)
    if tech_skills:
        # Count skills by department categories
        dept_scores = {}
        for skill in tech_skills.split(", "):
            skill_lower = skill.lower()
            
            # AI and Data Science related skills
            if any(term in skill_lower for term in ["python", "data", "machine learning", "tensorflow", 
                                                  "statistics", "ai", "analytics", "numpy", "pandas"]):
                dept_scores["Artificial Intelligence & Data Science"] = dept_scores.get("Artificial Intelligence & Data Science", 0) + 1
            
            # Web/Software Development related skills
            elif any(term in skill_lower for term in ["html", "css", "javascript", "web", "react", 
                                                     "angular", "node", "php", "django", "flask"]):
                dept_scores["Computer Science and Engineering"] = dept_scores.get("Computer Science and Engineering", 0) + 1
            
            # Electronics related skills
            elif any(term in skill_lower for term in ["circuit", "electrical", "electronics", 
                                                     "communication", "arduino", "vlsi"]):
                dept_scores["Electronics & Telecommunication Engineering"] = dept_scores.get("Electronics & Telecommunication Engineering", 0) + 1
            
            # Mechanical related skills
            elif any(term in skill_lower for term in ["mechanical", "machinery", "thermodynamics", 
                                                     "fluid", "autocad", "solidworks"]):
                dept_scores["Mechanical Engineering"] = dept_scores.get("Mechanical Engineering", 0) + 1
        
        # Return the department with the highest score
        if dept_scores:
            return max(dept_scores.items(), key=lambda x: x[1])[0]
    
    # Default to Computer Science if nothing else matches
    return "Computer Science and Engineering"

###################################################### CGPA ##################################################################

def extract_cgpa(text):
    # cgpa_pattern = r'\b(?:CGPA|GPA|cgpa|percent):\s*(\d+(?:\.\d+)?)\b'
    cgpa_pattern = r'\b(?:CGPA|GPA|cgpa|gpa|percentage|Percentage)[ :]*(\d+(?:\.\d{1,2})?)(?:/10)?\b'
    #     # 'cgpa': r'\b(?:CGPA|GPA|cgpa|gpa|percentage|Percentage)[ :]*(\d+(?:\.\d{1,2})?)(?:/10)?\b',

    match = re.search(cgpa_pattern, text, re.IGNORECASE)
    if match:
        cgpa = float(match.group(1))
        if 0 <= cgpa <= 10:
            return round(cgpa, 2)
    return None
###################################################### Marks ##################################################################

def extract_marks(text):
    doc = nlp(text)
    marks = {'ssc': None, 'hsc': None}
    current_context = None

    for token in doc:
        token_text = token.text.lower()
        if token_text in ['ssc', 'class x', 'cbse']:
            current_context = 'ssc'
        elif token_text in ['hsc', 'class xii']:
            current_context = 'hsc'

        if not token.like_num:
            continue

        if token.like_num:
            try:
                percentage = float(token.text)
            except:
                continue
            
            next_token = token.nbor() if token.i + 1 < len(doc) else None
            if (next_token and next_token.text == '%') or (0 <= percentage <= 100):
                if current_context:
                    marks[current_context] = percentage
                    current_context = None

    return marks['ssc'], marks['hsc']

###################################################### Hard Skills ##################################################################

def extract_skills(doc):
    """Advanced skills extraction using comprehensive skill list and vector similarity."""
    tech_skills = [
        "Python", "Java", "C++", "JavaScript", "TypeScript", "HTML", "CSS", "SQL", "React", "Angular", "Vue.js",
        "Node.js", "Express.js", "Django", "Flask", "Spring", "Ruby on Rails", "ASP.NET", "PHP", "Swift", "Kotlin",
        "Go", "Rust", "R", "Perl", "Scala", "MATLAB", "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Pandas",
        "NumPy", "Matplotlib", "Seaborn", "Plotly", "D3.js", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Firebase",
        "Heroku", "Linux", "Windows Server", "Bash", "Shell Scripting", "PowerShell", "Git", "SVN", "CI/CD", "Jenkins",
        "Ansible", "Chef", "Puppet", "Terraform", "Prometheus", "Grafana", "ELK Stack", "Splunk", "Redis", "RabbitMQ",
        "Kafka", "Hadoop", "Spark", "Flink", "Airflow", "Tableau", "Power BI", "QlikView", "Excel", "SAS", "SPSS",
        "MongoDB", "MySQL", "PostgreSQL", "SQLite", "Oracle", "Cassandra", "Couchbase", "Neo4j", "GraphQL", "REST",
        "SOAP", "gRPC", "OAuth", "JWT", "Blockchain", "Ethereum", "Solidity", "Hyperledger", "Cybersecurity",
        "Penetration Testing", "Network Security", "Cloud Security", "DevOps", "Agile", "Scrum", "Kanban", "JIRA",
        "Confluence", "Trello", "Asana", "Slack", "Microsoft Teams", "Adobe Creative Suite", "Photoshop", "Illustrator",
        "Figma", "Sketch", "InVision", "Blender", "AutoCAD", "SolidWorks", "Arduino", "Raspberry Pi", "IoT", "Embedded Systems",
        "Machine Learning", "Deep Learning", "Natural Language Processing", "Computer Vision", "Robotics", "Augmented Reality",
        "Virtual Reality", "Quantum Computing", "Game Development", "Unity", "Unreal Engine", "OpenGL", "WebGL",
        "Data Engineering", "Data Warehousing", "ETL", "Data Governance", "Data Modeling", "Big Data", "Data Science",
        "Artificial Intelligence", "Chatbots", "Sentiment Analysis", "Recommender Systems", "Time Series Analysis",
        "Statistical Analysis", "A/B Testing", "User Experience (UX)", "User Interface (UI)", "Responsive Design",
        "Accessibility", "SEO", "Content Management Systems (CMS)", "WordPress", "Drupal", "Joomla", "E-commerce",
        "Shopify", "WooCommerce", "Magento", "Salesforce", "CRM", "ERP", "SAP", "Oracle ERP", "Microsoft Dynamics",
        "Mobile Development", "iOS", "Android", "Flutter", "React Native", "Ionic", "Xamarin", "Progressive Web Apps (PWA)",
        "Microservices", "Serverless Architecture", "Event-Driven Architecture", "Monolithic Architecture", "API Development",
        "API Gateway", "Graph Databases", "NoSQL", "NewSQL", "In-Memory Databases", "Data Lakes", "Data Mesh",
        "DataOps", "MLOps", "AIOps", "Edge Computing", "Fog Computing", "Quantum Cryptography", "Post-Quantum Cryptography",
        "Homomorphic Encryption", "Differential Privacy", "Federated Learning", "Zero Trust Architecture", "Identity Management",
        "Single Sign-On (SSO)", "Multi-Factor Authentication (MFA)", "Biometrics", "Compliance", "GDPR", "HIPAA", "ISO/IEC 27001"
    ]

    # Prepare skills by converting to lowercase for case-insensitive matching
    skills_lower = {skill.lower(): skill for skill in tech_skills}

    # Function to check skill match using various techniques
    def find_skill_matches(doc_text):
        found_skills = set()
        doc_text_lower = doc_text.lower()

        # Direct word matching
        for skill_lower, skill in skills_lower.items():
            # Whole word matching with word boundaries
            if re.search(r'\b' + re.escape(skill_lower) + r'\b', doc_text_lower):
                found_skills.add(skill)

        return found_skills

    # Try different matching methods
    found_skills = find_skill_matches(doc.text)

    # If vector-based matching is desired, can add additional method
    if len(found_skills) < 5:
        # Vector-based similarity matching
        for skill in tech_skills:
            skill_vector = nlp(skill).vector
            if skill_vector.dot(doc.vector) > 0.5:
                found_skills.add(skill)

    # Sort and return skills
    return ', '.join(sorted(found_skills)) if found_skills else "None"

############################################################################soft skills############################################################

def extract_soft_skills(doc):
    """Extract soft skills with flexible and comprehensive matching."""
    soft_skills = set([
        # Leadership and Management
        "leadership", "team management", "strategic planning", "mentorship",
        "coaching", "decision making", "conflict resolution", "organizational skills",

        # Communication
        "communication", "public speaking", "presentation skills", "negotiation",
        "active listening", "written communication", "verbal communication",
        "cross-cultural communication", "storytelling",

        # Interpersonal Skills
        "teamwork", "collaboration", "networking", "relationship building",
        "emotional intelligence", "empathy", "interpersonal skills",
        "conflict management", "cultural awareness",

        # Problem-Solving and Analytical Skills
        "problem solving", "critical thinking", "analytical thinking",
        "creative problem solving", "strategic thinking", "innovation",
        "design thinking", "root cause analysis", "systems thinking",

        # Personal Effectiveness
        "time management", "adaptability", "resilience", "flexibility",
        "stress management", "self-motivation", "initiative", "proactivity",
        "continuous learning", "growth mindset",

        # Professional Attributes
        "professionalism", "work ethic", "attention to detail", "reliability",
        "accountability", "integrity", "customer service", "project coordination",

        # Emotional and Social Intelligence
        "emotional intelligence", "self-awareness", "social skills",
        "stress tolerance", "adaptability", "positive attitude",

        # Research and Analytical Skills
        "research skills", "data interpretation", "report writing",
        "strategic analysis", "market research", "trend analysis",

        # Creativity and Innovation
        "creativity", "innovative thinking", "brainstorming", "idea generation",
        "out-of-the-box thinking"
    ])

    found_soft_skills = set()
    text_lower = doc.text.lower()

    for skill in soft_skills:
        # More robust matching using regex to catch variations and context
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            found_soft_skills.add(skill.title())

    # Optional: Add weight to skills found multiple times
    skill_counts = {}
    for skill in found_soft_skills:
        skill_counts[skill] = text_lower.count(skill.lower())

    # Sort skills by their frequency if multiple skills found
    sorted_skills = sorted(
        found_soft_skills,
        key=lambda x: skill_counts.get(x, 0),
        reverse=True
    )

    return ', '.join(sorted_skills) if sorted_skills else "None"
#################################################################################pdf processing#######################################################

@st.cache_data
@st.cache_resource
def process_multiple_pdfs(uploaded_files):
    """Process multiple PDF files sequentially to extract relevant information."""
    processed_data = []

    for uploaded_file in uploaded_files:
        try:
            # Extract text from the PDF using pdfplumber
            text = extract_text_from_pdf(io.BytesIO(uploaded_file.read()))

            # Process the text to extract relevant information
            doc = nlp(text)
            department = extract_department(doc, text)
            name = extract_name(doc)
            email = extract_email(text)
            phone_number = extract_phone_number(text)
            degree = extract_degree(doc)
            department = department
            cgpa = extract_cgpa(text)
            marks_10th, marks_12th = extract_marks(text)
            tech_skills = extract_skills(doc)
            soft_skills = extract_soft_skills(doc)

            # Append the extracted information to the processed data list
            processed_data.append({
                "name": name,
                "email": email,
                "phone_number": phone_number,
                "degree": degree,
                "department": department,
                "cgpa": cgpa,
                "marks_10th": marks_10th,
                "marks_12th": marks_12th,
                "tech_skills": tech_skills,
                "soft_skills": soft_skills
            })
        except Exception as e:
            # Handle any exceptions that occur during processing
            print(f"Error processing file {uploaded_file.name}: {e}")

    return processed_data
##########################################################################dashboard##############################################################
def create_dashboard(df):
    st.title("Dashboard")

    valid_cgpa = df['cgpa'].dropna()
    avg_cgpa = valid_cgpa.mean() if not valid_cgpa.empty else 0

    valid_marks_10th = df['marks_10th'].dropna()
    avg_marks_10th = valid_marks_10th.mean() if not valid_marks_10th.empty else 0

    valid_marks_12th = df['marks_12th'].dropna()
    avg_marks_12th = valid_marks_12th.mean() if not valid_marks_12th.empty else 0

    st.sidebar.title("Filters")

    all_skills = set()
    for skills in df['tech_skills'].str.split(', '):
        if isinstance(skills, list):
            all_skills.update(skills)
    all_skills.discard('None')
    selected_skills = st.sidebar.multiselect('Filter by Skills', sorted(all_skills))

    departments = df['degree'].unique()
    selected_departments = st.sidebar.multiselect('Filter by Department', departments)

    cgpa_min, cgpa_max = float(df['cgpa'].min() if df['cgpa'].notna().any() else 0), float(df['cgpa'].max() if df['cgpa'].notna().any() else 10)
    cgpa_range = st.sidebar.slider('CGPA Range', cgpa_min, cgpa_max, (cgpa_min, cgpa_max))

    marks_10th_min, marks_10th_max = float(df['marks_10th'].min() if df['marks_10th'].notna().any() else 0), float(df['marks_10th'].max() if df['marks_10th'].notna().any() else 100)
    marks_10th_range = st.sidebar.slider('10th Percentage Range', marks_10th_min, marks_10th_max, (marks_10th_min, marks_10th_max))

    marks_12th_min, marks_12th_max = float(df['marks_12th'].min() if df['marks_12th'].notna().any() else 0), float(df['marks_12th'].max() if df['marks_12th'].notna().any() else 100)
    marks_12th_range = st.sidebar.slider('12th Percentage Range', marks_12th_min, marks_12th_max, (marks_12th_min, marks_12th_max))

    filtered_df = df.copy()
    if selected_skills:
        filtered_df = filtered_df[filtered_df['tech_skills'].apply(lambda x: any(skill in x.split(', ') for skill in selected_skills) if isinstance(x, str) else False)]
    if selected_departments:
        filtered_df = filtered_df[filtered_df['degree'].isin(selected_departments)]
    filtered_df = filtered_df[
        (filtered_df['cgpa'].fillna(cgpa_min).between(cgpa_range[0], cgpa_range[1], inclusive='both')) &
        (filtered_df['marks_10th'].fillna(marks_10th_min).between(marks_10th_range[0], marks_10th_range[1], inclusive='both')) &
        (filtered_df['marks_12th'].fillna(marks_12th_min).between(marks_12th_range[0], marks_12th_range[1], inclusive='both'))
    ]

    # First Row: KPIs
    col1, col2, col3 = st.columns(3, gap='medium')
    with col1:
        with st.container(border=True):
           st.metric("Total Students", len(filtered_df))
    with col2:
        with st.container(border=True):
           avg_cgpa = filtered_df['cgpa'].mean() if not filtered_df['cgpa'].isna().all() else 0
           st.metric("Average CGPA", f"{avg_cgpa:.2f}")
    with col3:
        with st.container(border=True):
           all_skills = [skill for skills in filtered_df['tech_skills'].str.split(', ') if isinstance(skills, list) for skill in skills if skill != 'None']
           top_skill = Counter(all_skills).most_common(1)[0][0] if all_skills else "N/A"
           st.metric("Top Skill", top_skill)

    # Second Row: Area Graph for All Technical Skills
    with st.container():
        all_skills = [skill for skills in filtered_df['tech_skills'].str.split(', ') if isinstance(skills, list) for skill in skills if skill != 'None']
        skills_count = Counter(all_skills)
        skills_df = pd.DataFrame.from_dict(skills_count, orient='index').reset_index()
        skills_df.columns = ['Skill', 'Count']
        fig_skills = px.area(skills_df.sort_values('Count', ascending=False),
                           x='Skill',
                           y='Count',
                           title='Technical Skills Distribution')
        fig_skills.update_layout(
            xaxis={'tickangle': 45},
        )
        st.plotly_chart(fig_skills, use_container_width=True)

    # Third Row: Line Graph for Soft Skills and Donut for CGPA
    col1, col2 = st.columns([2,1], gap="medium")
    with col1:
        with st.container():
            soft_skills = [skill for skills in filtered_df['soft_skills'].str.split(', ') if isinstance(skills, list) for skill in skills if skill != 'None']
            soft_skills_count = Counter(soft_skills)
            soft_skills_df = pd.DataFrame.from_dict(soft_skills_count, orient='index').reset_index()
            soft_skills_df.columns = ['Skill', 'Count']
            fig_soft = px.line(soft_skills_df,
                             x='Skill',
                             y='Count',
                             title='Soft Skills Distribution')
            st.plotly_chart(fig_soft, use_container_width=True)

    with col2:
        with st.container():
            cgpa_ranges = pd.cut(filtered_df['cgpa'],
                               bins=[0, 6, 7, 8, 9, 10],
                               labels=['<6', '6-7', '7-8', '8-9', '9-10'])
            cgpa_dist = cgpa_ranges.value_counts().sort_index()
            fig_cgpa = go.Figure(data=[go.Pie(labels=cgpa_dist.index,
                                            values=cgpa_dist.values,
                                            hole=.3)])
            fig_cgpa.update_layout(title='CGPA Distribution')
            st.plotly_chart(fig_cgpa, use_container_width=True)

    # Fourth Row: Bar Graph for Departments and Pie for 10th, 12th Percentage
    col1, col2, col3 = st.columns([2,1,1], gap='medium')
    with col1:
        with st.container():
            dept_count = filtered_df['department'].value_counts()
            fig_dept = px.bar(x=dept_count.index,
                            y=dept_count.values,
                            title='Department Distribution')
            st.plotly_chart(fig_dept, use_container_width=True)

    with col2:
        with st.container():
            marks_10th_bins = pd.cut(filtered_df['marks_10th'],
                                   bins=[0, 60, 70, 80, 90, 100],
                                   labels=['<60', '60-70', '70-80', '80-90', '90-100'])
            marks_10th_dist = marks_10th_bins.value_counts().sort_index()
            fig_10th = px.pie(names=marks_10th_dist.index,
                            values=marks_10th_dist.values,
                            title='10th Percentage Distribution')
            st.plotly_chart(fig_10th, use_container_width=True)

    with col3:
        with st.container():
            marks_12th_bins = pd.cut(filtered_df['marks_12th'],
                                   bins=[0, 60, 70, 80, 90, 100],
                                   labels=['<60', '60-70', '70-80', '80-90', '90-100'])
            marks_12th_dist = marks_12th_bins.value_counts().sort_index()
            fig_12th = px.pie(names=marks_12th_dist.index,
                            values=marks_12th_dist.values,
                            title='12th Percentage Distribution')
            st.plotly_chart(fig_12th, use_container_width=True)

    # Filtered Students Table
    st.markdown("### Filtered Students")
    display_df = filtered_df[['name', 'email', 'phone_number', 'degree', 'cgpa', 'department', 'marks_10th', 'marks_12th', 'tech_skills', 'soft_skills']]
    format_dict = {
        'phone_number': lambda x: str(x) if x is not None else "N/A",
        'cgpa': lambda x: "{:.2f}".format(x) if x is not None else "N/A",
        'marks_10th': lambda x: "{:.2f}".format(x) if x is not None else "N/A",
        'marks_12th': lambda x: "{:.2f}".format(x) if x is not None else "N/A"
    }
    st.dataframe(display_df.style.format(format_dict))

    if st.button("Export Filtered Data to CSV"):
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download Filtered CSV",
            data=csv,
            file_name="filtered_resume_data.csv",
            mime="text/csv",
        )


#####################################################################################################################################
def admin_function():
    st.markdown(STYLES["page_bg_img"], unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center;'>Interactive Resume Analyzer Dashboard</h1>", unsafe_allow_html=True)

    uploaded_files = st.file_uploader("Upload resumes (PDF, TXT)", type=['pdf', 'txt'], accept_multiple_files=True)

    if uploaded_files:
        # Add validation to check if at least 2 files are uploaded
        if len(uploaded_files) < 2:
            st.error("Please upload at least 2 resume files to proceed with analysis.")
            return

        # Use a single spinner for the entire processing block
        with st.spinner('Processing resumes...'):
            processed_data = process_multiple_pdfs(uploaded_files)
            df = pd.DataFrame(processed_data)

        if not df.empty:
            st.write(f"Total resumes uploaded: {len(uploaded_files)}")
            st.write(f"Successfully processed resumes: {len(df)}")
            create_dashboard(df)
        else:
            st.warning("No data extracted from the resumes.")
    else:
        st.warning("Please upload PDF or TXT resumes to proceed with extraction.")

if __name__ == "__main__":
    admin_function()








