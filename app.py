import streamlit as st
from pdf2image import convert_from_path
from PIL import Image
import os
import google.generativeai as genai
import mysql.connector as mysql
import PyPDF2 as pdf
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

# Configure Google Generative AI with API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input_text):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input_text)
    return response.text

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += str(page.extract_text())
    return text

# Set directory for saving images
SAVE_DIR = "saved_images"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# Prompt template
input_prompt = """
Hey Act Like a skilled or very experience ATS(Application Tracking System)
with a deep understanding of tech field,software engineering,data science ,data analyst
and big data engineer. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide 
best assistance for improving thr resumes. Assign the percentage Matching based 
on Jd and
the missing keywords with high accuracy
resume:{text}
description:{jd}
I want the response in one single string having the structure and also dont forget to give meanigfful response if 
ATS score is low give appropriate decision about Can apply also dont forget to give bullet points for improvement
**ATS Score**: "%"
**MissingKeyword**:\n [],\n
**Can Select**: " "
"""

# MySQL connection setup
def create_connection():
    return mysql.connect(
        host="localhost",
        user="root",
        password="Kajal@123",
    )

def create_database(cursor):
    cursor.execute("CREATE DATABASE IF NOT EXISTS ATS_resume")

def create_table(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ats_resume_info (
        id INT AUTO_INCREMENT PRIMARY KEY,
        _first_name VARCHAR(255),
        _last_name VARCHAR(255),
        _role VARCHAR(255),
        _score INT,
        _experience VARCHAR(255)
    )
    """)

con = create_connection()
cursor = con.cursor()

# Create database and table
create_database(cursor)
con.database = 'ATS_resume'  # Select database
create_table(cursor)

## Streamlit app

with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

if 'page' not in st.session_state:
    st.session_state.page = 'input'

def show_home_page():
    
    st.title(':rainbow[RESUME SPECTRUM]')
    first_name = st.text_input("Enter First Name:")
    last_name = st.text_input("Enter Last Name:")

    role = st.selectbox("Select a role: ", ["--Select--", "Data Analyst", "Data Scientist", "Machine Learning Engineer", "Data Engineer", "Software Engineer", "Full Stack Engineer"])

    experience = st.selectbox("Select an experience:", ["--Select--", "Fresher", "1-2 Years", "2-3 Years", "3-4 Years", "4-5 Years", "5-6 Years", "7-10 Years"])

    jd = st.text_area("Paste the Job Description")
    uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the pdf")

    submit = st.button("Submit")

    if submit :
        st.experimental_rerun()

    if uploaded_file is not None:
        st.session_state.page = 'result'
        st.session_state.uploaded_file = uploaded_file
        st.session_state.first_name = first_name
        st.session_state.last_name = last_name
        st.session_state.role = role
        st.session_state.experience = experience
        
    elif submit and uploaded_file is None:
        st.subheader("Please Upload your Resume")

def show_result_page():
    # Convert and save PDF file to images
    with open("temp.pdf", "wb") as f:
        f.write(st.session_state.uploaded_file.read())
    images = convert_from_path("temp.pdf")
    for i, image in enumerate(images):
        image_path = os.path.join(SAVE_DIR, f"page_{i+1}.png")
        image.save(image_path, "PNG")
    os.remove("temp.pdf")  # Delete the temp.pdf file

    text = input_pdf_text(st.session_state.uploaded_file)
    response = get_gemini_response(input_prompt)

    # Create two columns
    col1, col2 = st.columns((2,2), gap="large")

    # Display the resume images in the right column
    with col2:
        for i, image in enumerate(images):
            st.image(image, caption=f"Page {i+1}", use_column_width=True)

    # Display the ATS response in the left column
    with col1:
        st.subheader(response)

        import re
        match = re.search(r"ATS Score\*\*: (\d+)%", response)
        if match:
            ats_score_str = match.group(1)
            ats_score_int = int(ats_score_str)
        else:
            ats_score_str = "Not Provided by ATS"  # More informative default value

        sql = "INSERT INTO ats_resume_info (_first_name, _last_name, _role, _score, _experience) VALUES (%s, %s, %s, %s, %s)"
        values = (st.session_state.first_name, st.session_state.last_name, st.session_state.role, ats_score_int, st.session_state.experience)
        cursor.execute(sql, values)

        con.commit()
        st.success("Data Updated", icon="✅")

        back = st.button("Back")

        if back:
            st.experimental_rerun()
        st.session_state.page = 'input'

if st.session_state.page == 'input':
    show_home_page()
elif st.session_state.page == 'result':
    show_result_page()
