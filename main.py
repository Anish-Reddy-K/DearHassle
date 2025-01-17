import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import date
import tempfile
import base64
import json
from pathlib import Path
import PyPDF2
import io

# Load environment variables
load_dotenv()

def save_api_key(api_key):
    """Save API key to .env file"""
    env_path = Path('.env')
    if env_path.exists():
        with open(env_path, 'r') as f:
            lines = f.readlines()
        # Update existing OPENAI_API_KEY line or add new one
        key_updated = False
        for i, line in enumerate(lines):
            if line.startswith('OPENAI_API_KEY='):
                lines[i] = f'OPENAI_API_KEY={api_key}\n'
                key_updated = True
                break
        if not key_updated:
            lines.append(f'OPENAI_API_KEY={api_key}\n')
        with open(env_path, 'w') as f:
            f.writelines(lines)
    else:
        with open(env_path, 'w') as f:
            f.write(f'OPENAI_API_KEY={api_key}\n')

# Initialize OpenAI client with None - will be set when API key is provided
client = None

# Constants
CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "personal_info": {
        "full_name": "Your Name",
        "location": "City, Country",
        "phone": "123-456-7890",
        "email": "your.email@example.com",
        "linkedin": "https://linkedin.com/in/yourusername",
        "portfolio": "https://yourportfolio.com",
        "github": "https://github.com/yourusername"
    },
    "resume_path": "resume_context.txt",
    "templates": {
        "email": {
            "subject": "Follow-Up on {position_title} Application",
            "body": """Hi {hiring_manager_name},

I hope you are doing well. I recently applied for the {position_title} position, and wanted to check in on your decision timeline. I am very excited about the opportunity to join {company_name} and help {specific_work}

I understand how busy you probably are and want to thank you in advance for considering my application. Please let me know if I can provide any additional information.

I look forward to hearing from you soon.

Sincerely,
{full_name}"""
        },
        "linkedin": """Hi! I'm interested in the {position_title} role at {company_name}. My background includes {required_skills}. Looking forward to connecting!"""
    }
}

def load_config():
    """Load user configuration from JSON file"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Create default config if it doesn't exist
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
def ensure_templates_in_config(config):
    """Ensure templates exist in config, add them if missing"""
    if 'templates' not in config:
        config['templates'] = {
            "email": {
                "subject": "Follow-Up on {position_title} Application",
                "body": """Hi {hiring_manager_name},

I hope you are doing well. I recently applied for the {position_title} position, and wanted to check in on your decision timeline. I am very excited about the opportunity to join {company_name} and help {specific_work}

I understand how busy you probably are and want to thank you in advance for considering my application. Please let me know if I can provide any additional information.

I look forward to hearing from you soon.

Sincerely,
{full_name}"""
            },
            "linkedin": """Hi! I'm interested in the {position_title} role at {company_name}. My background includes {required_skills}. Looking forward to connecting!"""
        }
        save_config(config)
    return config

def save_config(config):
    """Save user configuration to JSON file"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def load_resume_context():
    """Load resume context from a text file"""
    config = load_config()
    try:
        with open(config['resume_path'], 'r') as f:
            return f.read()
    except FileNotFoundError:
        return None
    
def save_resume_context(content):
    """Save resume content to text file"""
    config = load_config()
    with open(config['resume_path'], 'w') as f:
        f.write(content)

def extract_text_from_pdf(pdf_file):
    """Extract text content from PDF file"""
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def settings_sidebar():
    """Create a settings sidebar for personal information and templates"""
    st.sidebar.title("Settings")
    
    # API Key Management
    if 'api_key' not in st.session_state:
        st.session_state.api_key = os.getenv('OPENAI_API_KEY', '')
    
    api_key = st.sidebar.text_input(
        "OpenAI API Key",
        value=st.session_state.api_key,
        type="password",
        help="Enter your OpenAI API key to use the application"
    )
    
    if api_key != st.session_state.api_key:
        st.session_state.api_key = api_key
        if api_key:
            save_api_key(api_key)
            st.sidebar.success("API key saved successfully!")
            st.rerun()
    
    if not api_key:
        st.error("Please enter your OpenAI API key in the sidebar to use the application.")
        st.stop()
    
    global client
    client = OpenAI(api_key=api_key)
    
    st.sidebar.divider()

    # Load current config and ensure templates exist
    config = load_config()
    config = ensure_templates_in_config(config)
    personal_info = config['personal_info']
    
    
    st.sidebar.subheader("Personal Information")
    updated_info = {}
    
    # Create input fields for each personal info field
    for key, value in personal_info.items():
        updated_info[key] = st.sidebar.text_input(
            key.replace('_', ' ').title(),
            value=value,
            key=f"settings_{key}"
        )
    
    # Template settings
    st.sidebar.divider()
    st.sidebar.subheader("Message Templates")
    
    with st.sidebar.expander("Email Templates"):
        email_subject = st.text_input(
            "Email Subject Template",
            value=config['templates']['email']['subject'],
            help="Use {placeholder} format. Available: {position_title}, {company_name}, etc."
        )
        email_body = st.text_area(
            "Email Body Template",
            value=config['templates']['email']['body'],
            height=200,
            help="Use {placeholder} format. Available: all job_info and personal_info fields"
        )
    
    with st.sidebar.expander("LinkedIn Template"):
        linkedin_message = st.text_area(
            "LinkedIn Message Template",
            value=config['templates']['linkedin'],
            height=100,
            help="Use {placeholder} format. Must be under 200 characters"
        )
    
    # Update the save button section
    if st.sidebar.button("Save All Settings"):
        config['personal_info'] = updated_info
        config['templates']['email']['subject'] = email_subject
        config['templates']['email']['body'] = email_body
        config['templates']['linkedin'] = linkedin_message
        save_config(config)
        st.sidebar.success("All settings saved successfully!")
        st.rerun()

def resume_uploader():
    """Handle resume upload functionality"""
    uploaded_file = st.file_uploader("Upload your resume (TXT or PDF format)", type=['txt', 'pdf'])
    
    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            content = extract_text_from_pdf(uploaded_file)
        else:
            content = uploaded_file.getvalue().decode()
        save_resume_context(content)
        st.success("Resume uploaded successfully!")
        return content
    
    return load_resume_context()

def generate_linkedin_message(job_info: dict, config: dict) -> str:
    """Generate LinkedIn connection message using template"""
    try:
        # Get template from config
        template = config['templates']['linkedin']
        
        # Create format dict with all possible placeholders
        format_dict = {
            **job_info,
            **config['personal_info'],
            'required_skills': job_info['required_skills'].split('<br/>')[0].strip('• ')  # Take first skill only due to character limit
        }
        
        # Format the template
        message = template.format(**format_dict)
        
        # Ensure message is under 200 characters
        if len(message) > 200:
            message = message[:197] + "..."
        return message
    except Exception as e:
        st.error(f"Error generating LinkedIn message: {str(e)}")
        return f"Hi! I'm interested in the {job_info['position_title']} role at {job_info['company_name']}. Looking forward to connecting!"
    
def extract_job_info(job_description: str, resume_context: str) -> dict:
    """Extract relevant information from job description using GPT-4"""
    try:
        system_prompt = """You are an expert AI career consultant. Your task is to:
        1. Analyze the provided job description
        2. Review the candidate's resume
        3. Identify key matches and alignment between the two
        
        Return a JSON object with the following structure:
        {
            "company_name": "Name of the company",
            "position_title": "Title of the position",
            "hiring_manager_name": "Name if available, otherwise 'Hiring Manager'",
            "specific_work": "Brief description of specific work/responsibilities (1 sentence)",
            "required_skills": "Bullet points of 5-7 most important required skills, separated by <br/>",
            "company_mission": "Company mission or focus area from the description",
            "candidate_matches": "5 strongest matches between resume and job requirements, separated by <br/>"
        }

        Focus on technical skills, quantifiable achievements, and specific experience that directly relates to the role."""

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"""
                Job Description:
                {job_description}

                Candidate's Resume:
                {resume_context}
                """}
            ],
            temperature=0.7
        )
        
        try:
            return json.loads(completion.choices[0].message.content)
        except json.JSONDecodeError:
            content = completion.choices[0].message.content
            start = content.find('{')
            end = content.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(content[start:end])
            raise
            
    except Exception as e:
        st.error(f"Error extracting job information: {str(e)}")
        return {
            "company_name": "Company Name",
            "position_title": "Position Title",
            "hiring_manager_name": "Hiring Manager",
            "specific_work": "contribute to the team's projects",
            "required_skills": "• Required skill 1<br/>• Required skill 2<br/>• Required skill 3",
            "company_mission": "company mission and values",
            "candidate_matches": "• Match 1<br/>• Match 2<br/>• Match 3<br/>• Match 4<br/>• Match 5"
        }
    
def generate_email(job_info: dict, config: dict) -> tuple:
    """Generate follow-up email using template"""
    try:
        # Get templates from config
        subject_template = config['templates']['email']['subject']
        body_template = config['templates']['email']['body']
        
        # Create format dict with all possible placeholders
        format_dict = {
            **job_info,
            **config['personal_info']
        }
        
        # Format the templates
        subject = subject_template.format(**format_dict)
        body = body_template.format(**format_dict)
        
        return subject, body
    except Exception as e:
        st.error(f"Error generating email: {str(e)}")
        return (f"Follow-Up on {job_info['position_title']} Application",
                f"Hi {job_info['hiring_manager_name']},\n\nFollowing up on my {job_info['position_title']} application.\n\nBest,\n{config['personal_info']['full_name']}")

def generate_cv_content(job_info: dict, resume_context: str) -> dict:
    """Generate CV content using GPT-4"""
    try:
        system_prompt = """You are an expert CV writer for tech industry applications. 

Generate highly tailored CV content based on the candidate's resume and job details.

Your response must strictly follow this structure with exact section names, so it can be programmatically processed:

about_me: 
A powerful opening statement highlighting relevant experience and achievements. 
(Write content here)

why_company: 
A compelling argument for why the candidate is interested in and suitable for this specific company.
(Write content here)

why_me: 
5 specific bullet points showing concrete examples of how the candidate's experience matches the role.
• (Write bullet point 1 here)
• (Write bullet point 2 here)
• (Write bullet point 3 here)
• (Write bullet point 4 here)
• (Write bullet point 5 here)

Guidelines:
- Use active voice and specific metrics.
- Focus on achievements and impact.
- Make direct connections between past experience and job requirements.
- Be specific about technical skills and tools.
- Highlight relevant projects and their outcomes.
"""

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"""
                Job Information:
                {json.dumps(job_info, indent=2)}
                
                Candidate's Resume:
                {resume_context}
                """}
            ],
            temperature=0.7
        )
        
        return {
            'about_me': completion.choices[0].message.content.split('why_company')[0].replace('about_me:', '').strip(),
            'why_company': completion.choices[0].message.content.split('why_company:')[1].split('why_me:')[0].strip(),
            'why_me': completion.choices[0].message.content.split('why_me:')[1].strip()
        }
    except Exception as e:
        st.error(f"Error generating CV content: {str(e)}")
        return {
            'about_me': "Default about me section",
            'why_company': "Default why company section",
            'why_me': "• Default bullet point 1\n• Default bullet point 2\n• Default bullet point 3\n• Default bullet point 4\n• Default bullet point 5"
        }

def generate_cv_pdf(job_info: dict, cv_content: dict) -> str:
    """Generate PDF CV and return as base64 string"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        doc = SimpleDocTemplate(
            tmp_file.name,
            pagesize=LETTER,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )
        
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Header', parent=styles['Heading1'], alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='ContactInfo', parent=styles['Normal'], alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='LinkStyle', parent=styles['ContactInfo'], alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='Position', parent=styles['Normal'], underline=True))
        styles.add(ParagraphStyle(name='SubHeading', parent=styles['Heading3']))
        
        elements = []
        
        # Header
        elements.append(Paragraph("Anish Reddy", styles['Header']))
        elements.append(Paragraph("Waterloo, Canada", styles['ContactInfo']))
        elements.append(Spacer(1, 5))
        
        # Contact Info
        contact_info = (
            "437-557-2209 | "
            '<font color="blue"><u><link href="https://linkedin.com/in/anishreddyk">LinkedIn</link></u></font> | '
            '<font color="blue"><u><link href="https://anishreddyk.com">Portfolio</link></u></font> | '
            '<font color="blue"><u><link href=https://github.com/Anish-Reddy-K">Github</link></u></font> | '
            '<font color="blue"><u><link href="mailto:anishreddy3456@gmail.com">anishreddy3456@gmail.com</link></u></font>'
        )
        elements.append(Paragraph(contact_info, styles['LinkStyle']))
        elements.append(Spacer(1, 30))
        
        # Date and Company
        date_today = date.today().strftime("%B %d, %Y")
        header_data = [[f"{job_info['company_name']} Recruitment Team", date_today]]
        header_table = Table(header_data, colWidths=[doc.width/2, doc.width/2])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 30))
        
        # Position
        elements.append(Paragraph(f"<u><b>Job application for {job_info['position_title']}</b></u>", styles['Position']))
        elements.append(Spacer(1, 20))
        
        # Greeting
        elements.append(Paragraph(f"Dear {job_info['hiring_manager_name']},", styles['Normal']))
        elements.append(Spacer(1, 5))
        
        # Content sections
        for section_title, content in [
            ("About Me", cv_content['about_me']),
            (f"Why {job_info['company_name']}?", cv_content['why_company']),
            ("Why Me?", cv_content['why_me'].replace('\n', '<br/>'))
        ]:
            elements.append(Paragraph(section_title, styles['SubHeading']))
            elements.append(Paragraph(content, styles['Normal']))
            elements.append(Spacer(1, 10))
        
        # Signature
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Sincerely,", styles['Normal']))
        elements.append(Paragraph("Anish Reddy", styles['Normal']))
        
        doc.build(elements)
        
        with open(tmp_file.name, "rb") as pdf_file:
            encoded_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
        
        os.unlink(tmp_file.name)
        return encoded_pdf

def main():
    st.title("Job Application Generator")

    # Add settings sidebar
    settings_sidebar()
    
    # Handle resume upload and display current resume
    resume_context = resume_uploader()

    if resume_context is None:
        st.warning("Please upload your resume to continue.")
        st.stop()
    else:
        st.success("Resume loaded successfully!")
        with st.expander("View/Edit Current Resume"):
            edited_resume = st.text_area("Edit your resume:", value=resume_context, height=400)
            if st.button("Apply Changes"):
                save_resume_context(edited_resume)
                st.success("Resume updated successfully!")
                resume_context = edited_resume

    st.write("Paste your job description below to generate a customized email and CV")
    
    job_description = st.text_area("Job Description:", height=200)
    
    if st.button("Generate Documents", type="primary") and job_description:
        with st.spinner('Analyzing job description and generating documents...'):
            st.session_state.job_info = extract_job_info(job_description, resume_context)
            config = load_config()
            # Generate all documents at once
            st.session_state.cv_content = generate_cv_content(st.session_state.job_info, resume_context)
            subject, body = generate_email(st.session_state.job_info, config)
            st.session_state.email_content = {"subject": subject, "body": body}
            st.session_state.linkedin_message = generate_linkedin_message(st.session_state.job_info, config)
    
    if hasattr(st.session_state, 'job_info'):
        if 'current_tab' not in st.session_state:
            st.session_state.current_tab = "Cover Letter"

        st.session_state.current_tab = st.radio(
            "Select Document",
            ["Cover Letter", "Follow-up Email", "LinkedIn Message"],
            horizontal=True,
            label_visibility="hidden",
            index=0 if st.session_state.current_tab == "Cover Letter" else 
                  1 if st.session_state.current_tab == "Follow-up Email" else 2
        )
        
        st.divider()
        
        if st.session_state.current_tab == "Cover Letter":
            st.subheader("Edit CV")
            
            edited_about_me = st.text_area(
                "About Me",
                value=st.session_state.cv_content['about_me'],
                height=150
            )
            edited_why_company = st.text_area(
                f"Why {st.session_state.job_info['company_name']}?",
                value=st.session_state.cv_content['why_company'],
                height=150
            )
            edited_why_me = st.text_area(
                "Why Me? (Each point in a new line)",
                value=st.session_state.cv_content['why_me'],
                height=150
            )
            
            edited_cv_content = {
                'about_me': edited_about_me,
                'why_company': edited_why_company,
                'why_me': edited_why_me
            }
            
            if st.button("Preview CV"):
                st.session_state.cv_pdf = generate_cv_pdf(st.session_state.job_info, edited_cv_content)
            
            if hasattr(st.session_state, 'cv_pdf'):
                st.subheader("CV Preview")
                pdf_display = f'<iframe src="data:application/pdf;base64,{st.session_state.cv_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
                
                st.download_button(
                    label="Download",
                    data=base64.b64decode(st.session_state.cv_pdf),
                    file_name=f"{st.session_state.job_info['company_name'].lower().replace(' ', '_')}_Cover_Letter.pdf",
                    mime="application/pdf"
                )
                
        elif st.session_state.current_tab == "Follow-up Email":
            st.subheader("Subject:")
            st.code(st.session_state.email_content["subject"], language=None)
            st.subheader("Email Body:")
            st.code(st.session_state.email_content["body"], language=None, wrap_lines=True)
        else:  # LinkedIn Message
            st.subheader("LinkedIn Connection Message:")
            st.code(st.session_state.linkedin_message, language=None, wrap_lines=True)
            st.caption(f"Character count: {len(st.session_state.linkedin_message)}/200")

if __name__ == "__main__":
    main()