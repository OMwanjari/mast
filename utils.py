import io
import re
import PyPDF2

# Student page
def process_single_pdf(uploaded_file):
    if uploaded_file is None:
        raise FileNotFoundError("No file uploaded")

    pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

    return text


def extract_score_and_feedback(result_text):
    score = 0
    feedback = "No feedback available."
    
    score_patterns = [
        r'(\d+)%',  
        r'(\d+)/100',  
        r'(\d+) out of 100',  
        r'score of (\d+)',  
        r'rate this resume a (\d+)',  
    ]
    
    for pattern in score_patterns:
        match = re.search(pattern, result_text, re.IGNORECASE)
        if match:
            score = int(match.group(1))
            if pattern.endswith(r'(\d+)') and score <= 10:
                score *= 10
            break
    
    feedback_patterns = [
        r'(\d+)%\.?\s*(.+)',  
        r'Overall,?\s*(.+)',  
        r'In summary,?\s*(.+)',  
        r'(?<=\n)(?!(\d+%|score:))(.+)',  
    ]
    
    for pattern in feedback_patterns:
        match = re.search(pattern, result_text, re.DOTALL | re.IGNORECASE)
        if match:
            feedback = match.group(1) if len(match.groups()) == 1 else match.group(2)
            feedback = feedback.strip()
            break
    
    return score, feedback