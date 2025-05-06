import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import io
import base64
from reportlab.platypus import Frame, PageTemplate
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from PIL import Image as PILImage

def main():
    st.set_page_config(page_title="Resume Builder", layout="wide")
    
    # Initialize session state for tracking the application flow
    if 'page' not in st.session_state:
        st.session_state.page = 'select_type'
    
    # Initial page to select resume type
    if st.session_state.page == 'select_type':
        st.title("Professional Resume Builder")
        st.write("Choose your resume type:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Resume with Profile Picture", use_container_width=True):
                st.session_state.include_image = True
                st.session_state.page = 'resume_builder'
                st.rerun()
                
        with col2:
            if st.button("Resume without Profile Picture", use_container_width=True):
                st.session_state.include_image = False
                st.session_state.page = 'resume_builder'
                st.rerun()
    
    # Resume builder page
    elif st.session_state.page == 'resume_builder':
        st.title("Professional Resume Builder")
        st.write("Fill in your details to generate a professional resume")
        
        # Personal Information
        st.header("Personal Information")
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone Number")
        
        with col2:
            linkedin = st.text_input("LinkedIn (optional)")
            github = st.text_input("GitHub (optional)")
            website = st.text_input("Personal Website (optional)")
        
        # Profile Picture section (only if include_image is True)
        if st.session_state.include_image:
            st.header("Profile Picture")
            uploaded_file = st.file_uploader("Upload a profile picture", type=["jpg", "jpeg", "png"])
            
            if uploaded_file is not None:
                # Display the uploaded image
                image = PILImage.open(uploaded_file)
                st.image(image, caption="Uploaded Profile Picture", width=200)
                
                # Save the image to session state
                st.session_state.profile_image = uploaded_file.getvalue()
            elif 'profile_image' in st.session_state:
                # Display previously uploaded image
                image = PILImage.open(io.BytesIO(st.session_state.profile_image))
                st.image(image, caption="Uploaded Profile Picture", width=200)
        
        # Education section
        st.header("Education")
        st.write("Add your educational background")
        
        education_data = []
        
        # Initialize session state for education
        if 'education_count' not in st.session_state:
            st.session_state.education_count = 1
        
        def add_education():
            st.session_state.education_count += 1
        
        for i in range(st.session_state.education_count):
            st.subheader(f"Education #{i+1}")
            col1, col2 = st.columns(2)
            with col1:
                institution = st.text_input(f"Institution {i+1}")
                degree = st.text_input(f"Degree {i+1}")
            with col2:
                start_date = st.text_input(f"Start Date {i+1}")
                end_date = st.text_input(f"End Date {i+1}")
            gpa = st.text_input(f"GPA {i+1} (optional)")
            
            if institution or degree:
                education_data.append({
                    "Institution": institution,
                    "Degree": degree,
                    "Start Date": start_date,
                    "End Date": end_date,
                    "GPA": gpa
                })
            
            st.divider()
        
        st.button("Add Another Education", on_click=add_education)
        
        # Skills section
        st.header("Skills")
        
        technical_skills = st.text_area("Technical Skills (separate with commas)", height=100)
        soft_skills = st.text_area("Soft Skills (separate with commas)", height=100)
        languages = st.text_area("Languages (separate with commas)", height=75)
        
        # Projects section
        st.header("Projects")
        
        projects_data = []
        
        # Initialize session state for projects
        if 'project_count' not in st.session_state:
            st.session_state.project_count = 1
        
        def add_project():
            st.session_state.project_count += 1
        
        for i in range(st.session_state.project_count):
            st.subheader(f"Project #{i+1}")
            project_name = st.text_input(f"Project Name {i+1}")
            project_description = st.text_area(f"Description {i+1}", height=100)
            tech_used = st.text_input(f"Technologies Used {i+1}")
            project_link = st.text_input(f"Project Link {i+1} (optional)")
            
            if project_name or project_description:
                projects_data.append({
                    "Name": project_name,
                    "Description": project_description,
                    "Technologies": tech_used,
                    "Link": project_link
                })
            
            st.divider()
        
        st.button("Add Another Project", on_click=add_project)
        
        # Certificates section
        st.header("Certificates")
        
        certificates_data = []
        
        # Initialize session state for certificates
        if 'certificate_count' not in st.session_state:
            st.session_state.certificate_count = 1
        
        def add_certificate():
            st.session_state.certificate_count += 1
        
        for i in range(st.session_state.certificate_count):
            st.subheader(f"Certificate #{i+1}")
            col1, col2 = st.columns(2)
            with col1:
                cert_name = st.text_input(f"Certificate Name {i+1}")
                issuer = st.text_input(f"Issuing Organization {i+1}")
            with col2:
                issue_date = st.text_input(f"Issue Date {i+1}")
                expiry_date = st.text_input(f"Expiry Date {i+1} (if applicable)")
            
            if cert_name or issuer:
                certificates_data.append({
                    "Name": cert_name,
                    "Issuer": issuer,
                    "Issue Date": issue_date,
                    "Expiry Date": expiry_date
                })
            
            st.divider()
        
        st.button("Add Another Certificate", on_click=add_certificate)
        
        # Generate Resume Button
        st.header("Generate Your Resume")
        resume_style = st.selectbox("Choose Resume Style", ["Professional", "Modern", "Minimalist"])
        
        if st.button("Generate Resume"):
            # Check if name and email are filled (minimum required fields)
            if not name or not email:
                st.error("Please fill in at least your name and email address.")
            else:
                # Check if image is required but not provided
                if st.session_state.include_image and 'profile_image' not in st.session_state:
                    st.error("Please upload a profile picture.")
                else:
                    # Get image data if available
                    image_data = st.session_state.get('profile_image', None) if st.session_state.include_image else None
                    
                    pdf = generate_resume(
                        name, email, phone, linkedin, github, website,
                        education_data, 
                        technical_skills, soft_skills, languages,
                        projects_data, 
                        certificates_data,
                        resume_style,
                        image_data
                    )
                    
                    # Create download button
                    st.success("Resume generated successfully!")
                    st.download_button(
                        label="Download Resume as PDF",
                        data=pdf,
                        file_name=f"{name.replace(' ', '_')}_Resume.pdf",
                        mime="application/pdf"
                    )
        
        # Option to go back to selection page
        if st.button("⬅️ Start Over"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.page = 'select_type'
            st.rerun()

def generate_resume(name, email, phone, linkedin, github, website,
                   education_data, technical_skills, soft_skills, languages,
                   projects_data, certificates_data, style, image_data=None):
    # Create a BytesIO buffer
    buffer = io.BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Add custom styles based on selected resume style
    if style == "Professional":
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.navy,
            spaceAfter=12,
            alignment=TA_LEFT if image_data else TA_CENTER  # Left alignment for name with image, center without
        )
        section_style = ParagraphStyle(
            'Section',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.darkblue,
            spaceBefore=12,
            spaceAfter=6
        )
        contact_style = ParagraphStyle(
            'Contact',
            parent=styles['Normal'],
            fontSize=9,  # Smaller font for contact info
            alignment=TA_LEFT if image_data else TA_CENTER  # Left alignment with image, center without
        )
    elif style == "Modern":
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.black,
            spaceAfter=12,
            alignment=TA_LEFT if image_data else TA_CENTER  # Left alignment for name with image, center without
        )
        section_style = ParagraphStyle(
            'Section',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.gray,
            spaceBefore=14,
            spaceAfter=8
        )
        contact_style = ParagraphStyle(
            'Contact',
            parent=styles['Normal'],
            fontSize=10,  # Smaller font for contact info
            alignment=TA_LEFT if image_data else TA_CENTER  # Left alignment with image, center without
        )
    else:  # Minimalist
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.black,
            spaceAfter=10,
            alignment=TA_LEFT if image_data else TA_CENTER  # Left alignment for name with image, center without
        )
        section_style = ParagraphStyle(
            'Section',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.black,
            spaceBefore=10,
            spaceAfter=5
        )
        contact_style = ParagraphStyle(
            'Contact',
            parent=styles['Normal'],
            fontSize=9,  # Smaller font for contact info
            alignment=TA_LEFT if image_data else TA_CENTER  # Left alignment with image, center without
        )
    
    # Date style for right alignment
    date_style = ParagraphStyle(
        'Date',
        parent=styles['Normal'],
        alignment=TA_RIGHT
    )
    
    # Create content elements list
    elements = []
    
    # For resume with image, create a table with image and contact info
    if image_data:
        # Process the image
        image_stream = io.BytesIO(image_data)
        img = Image(image_stream, width=1.5*inch, height=1.5*inch)
        
        # Create a table for image and name/contact info with image on right
        header_data = [
            [Paragraph(name, title_style), img]
        ]
        
        # Contact Information
        contact_parts = []
        if email:
            contact_parts.append(f"Email: {email}")
        if phone:
            contact_parts.append(f"Phone: {phone}")
        if linkedin:
            contact_parts.append(f"LinkedIn: {linkedin}")
        if github:
            contact_parts.append(f"GitHub: {github}")
        if website:
            contact_parts.append(f"Website: {website}")
        
        contact_text = "<br/>".join(contact_parts)  # Use line breaks for contact info
        header_data.append([Paragraph(contact_text, contact_style), ""])
        
        # Create the table with image on right
        header_table = Table(header_data, colWidths=[4*inch, 2*inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),  # Right-align the image column
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),   # Left-align the text column
            ('SPAN', (1, 0), (1, 1)),  # Span the image cell across rows
        ]))
        
        elements.append(header_table)
    else:
        # Header with name - centered (for resume without image)
        elements.append(Paragraph(name, title_style))
        
        # Contact Information - centered with smaller font
        contact_parts = []
        if email:
            contact_parts.append(f"Email: {email}")
        if phone:
            contact_parts.append(f"Phone: {phone}")
        if linkedin:
            contact_parts.append(f"LinkedIn: {linkedin}")
        if github:
            contact_parts.append(f"GitHub: {github}")
        if website:
            contact_parts.append(f"Website: {website}")
        
        contact_text = " • ".join(contact_parts)
        elements.append(Paragraph(contact_text, contact_style))
    
    # Add a spacer after the header
    elements.append(Spacer(1, 12))
    
    # Education Section
    if education_data:
        elements.append(Paragraph("Education", section_style))
        for edu in education_data:
            # Create a table for education with dates on right
            edu_table_data = []
            
            # Main education info
            edu_info = f"<b>{edu['Institution']}</b>"
            if edu['Degree']:
                edu_info += f" - {edu['Degree']}"
# Create a table for education with dates on right
            edu_table_data = []
            
            # Main education info
            edu_info = f"<b>{edu['Institution']}</b>"
            if edu['Degree']:
                edu_info += f" - {edu['Degree']}"
            if edu['GPA']:
                edu_info += f" | GPA: {edu['GPA']}"
            
            # Date info (right-aligned)
            date_info = ""
            if edu['Start Date'] or edu['End Date']:
                date_info = f"{edu['Start Date']} - {edu['End Date']}"
            
            edu_table_data.append([
                Paragraph(edu_info, styles['Normal']),
                Paragraph(date_info, date_style)
            ])
            
            # Create the table
            edu_table = Table(edu_table_data, colWidths=[4.5*inch, 2.5*inch])
            edu_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),   # Left-align the text column
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),  # Right-align the date column
            ]))
            
            elements.append(edu_table)
            elements.append(Spacer(1, 6))
    
    # Skills Section
    if technical_skills or soft_skills or languages:
        elements.append(Paragraph("Skills", section_style))
        
        if technical_skills:
            skill_text = f"<b>Technical Skills</b> - {technical_skills}"
            elements.append(Paragraph(skill_text, styles['Normal']))
            elements.append(Spacer(1, 6))
        
        if soft_skills:
            skill_text = f"<b>Soft Skills</b> - {soft_skills}"
            elements.append(Paragraph(skill_text, styles['Normal']))
            elements.append(Spacer(1, 6))
        
        if languages:
            skill_text = f"<b>Languages</b> - {languages}"
            elements.append(Paragraph(skill_text, styles['Normal']))
            elements.append(Spacer(1, 6))
    
    # Projects Section
    if projects_data:
        elements.append(Paragraph("Projects", section_style))
        for project in projects_data:
            project_info = f"<b>{project['Name']}</b>"
            if project['Technologies']:
                project_info += f" | <i>{project['Technologies']}</i>"
            if project['Link']:
                project_info += f" | <a href='{project['Link']}'>Project Link</a>"
            
            elements.append(Paragraph(project_info, styles['Normal']))
            elements.append(Paragraph(project['Description'], styles['Normal']))
            elements.append(Spacer(1, 6))
    
    # Certificates Section
    if certificates_data:
        elements.append(Paragraph("Certificates", section_style))
        for cert in certificates_data:
            # Create a table for certificate with dates on right
            cert_table_data = []
            
            # Main certificate info
            cert_info = f"<b>{cert['Name']}</b>"
            if cert['Issuer']:
                cert_info += f" | {cert['Issuer']}"
            
            # Date info (right-aligned)
            date_info = ""
            if cert['Issue Date']:
                date_info = f"Issued: {cert['Issue Date']}"
            if cert['Expiry Date']:
                date_info += f" | Expires: {cert['Expiry Date']}" if date_info else f"Expires: {cert['Expiry Date']}"
            
            cert_table_data.append([
                Paragraph(cert_info, styles['Normal']),
                Paragraph(date_info, date_style)
            ])
            
            # Create the table
            cert_table = Table(cert_table_data, colWidths=[4.5*inch, 2.5*inch])
            cert_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),   # Left-align the text column
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),  # Right-align the date column
            ]))
            
            elements.append(cert_table)
            elements.append(Spacer(1, 6))
    
    # Build the PDF
    doc.build(elements)
    
    # Get the PDF content from the buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf

if __name__ == "__main__":
    main()