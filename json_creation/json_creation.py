import io
import re
import json
import PyPDF2

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_name(text):
    lines = text.split('\n')
    
    for line in lines[:5]:  
        line = re.sub(r'[^a-zA-Z\s]', '', line).strip()
        words = line.split()
        if len(words) >= 2:
            return ' '.join(words[:2])
        elif len(words) == 1 and len(words[0]) >= 2:
            return words[0]
    
    return "Unknown"

def extract_skills(text):
    skills = set(["Python", "Java", "C++", "JavaScript", "HTML", "CSS", "SQL", "React", "Angular", "Node.js",
        "Ruby", "PHP", "Swift", "Kotlin", "C#", "R", "Go", "TypeScript", "Vue.js", "Django", "Flask",
        "Spring", "Express.js", "Bootstrap", "Tailwind", "SASS", "LESS", "Perl", "Scala", "Rust",
        "Matlab", "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Pandas", "NumPy", "Matplotlib",
        "Seaborn", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Linux", "Windows Server", "Jenkins",
        "Git", "SVN", "CI/CD", "Ansible", "Chef", "Puppet", "Terraform", "Shell Scripting",
        "PowerShell", "Salesforce", "SAP", "Oracle", "MongoDB", "MySQL", "PostgreSQL", "Firebase",
        "Redis", "Elasticsearch", "Kafka", "RabbitMQ", "Hadoop", "Spark", "Tableau", "Power BI",
        "Excel", "Data Analysis", "Machine Learning", "Deep Learning", "Artificial Intelligence",
        "Natural Language Processing", "Computer Vision", "Blockchain", "IoT", "Cybersecurity",
        "Penetration Testing", "Network Security", "Cloud Security", "DevOps", "Agile", "Scrum",
        "Project Management", "Leadership", "Communication", "Teamwork", "Problem Solving",
        "Critical Thinking", "Time Management"])
    
    found_skills = set()
    for skill in skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
            found_skills.add(skill)
    return ', '.join(sorted(found_skills))

def extract_experience(text):
    experience_patterns = [
        r'(\d+(?:\.\d+)?)(?:\+)?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp)',
        r'experience\s+of\s+(\d+(?:\.\d+)?)(?:\+)?\s*(?:years?|yrs?)',
        r'worked\s+for\s+(\d+(?:\.\d+)?)(?:\+)?\s*(?:years?|yrs?)'
    ]
    for pattern in experience_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    entry_level_keywords = ['entry level', 'fresh graduate', 'recent graduate', 'internship']
    if any(keyword in text.lower() for keyword in entry_level_keywords):
        return 0
    return 0 

def extract_education(text):
    education_patterns = {
        'PhD': r'\b(Ph\.?D\.?|Doctor of Philosophy)\b',
        'Master': r'\b(Master\'?s?|M\.?S\.?|M\.?Eng\.?|MBA)\b',
        'Bachelor': r'\b(Bachelor\'?s?|B\.?S\.?|B\.?E\.?|B\.?Tech\.?)\b'
    }
    for level, pattern in education_patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            return level
    return "Unknown"

def extract_projects(text):
    project_section = re.search(r'(?i)projects?:?(.*?)(?:\n\n|\Z)', text, re.DOTALL)
    if project_section:
        projects = re.findall(r'(?i)[-•]?\s*(.*?)(?=\n[-•]|\Z)', project_section.group(1))
        return '; '.join(project.strip() for project in projects if project.strip())
    return "No projects found"

def process_resume(file):
    text = extract_text_from_pdf(file)
    name = extract_name(text)
    skills = extract_skills(text)
    experience = extract_experience(text)
    education = extract_education(text)
    projects = extract_projects(text)
    return {
        "name": name,
        "skills": skills,
        "experience": experience,
        "education": education,
        "projects": projects
    }

def create_dataset_from_resumes(file_paths, output_json):
    data = []
    for file_path in file_paths:
        with open(file_path, 'rb') as file:
            resume_data = process_resume(file)
            data.append(resume_data)
    
    with open(output_json, 'w') as f:
        json.dump(data, f, indent=4)

import os

# Directory containing the resume files
resume_directory = "E:/llm tuning/test"

# List of PDF resume file paths
file_paths = [os.path.join(resume_directory, file) for file in os.listdir(resume_directory) if file.endswith('.pdf')]

# Output JSON file
output_json = "resumes_dataset.json"

create_dataset_from_resumes(file_paths, output_json)






































































































































































