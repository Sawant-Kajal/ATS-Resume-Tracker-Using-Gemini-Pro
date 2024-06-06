import streamlit as st
import google.generativeai as genai
import os
import mysql.connector as c
import PyPDF2 as pdf
from dotenv import load_dotenv


load_dotenv() ## load all our environment variables

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_repsonse(input):
    model=genai.GenerativeModel('gemini-pro')
    response=model.generate_content(input)
    return response.text

def input_pdf_text(uploaded_file):
    reader=pdf.PdfReader(uploaded_file)
    text=""
    for page in range(len(reader.pages)):
        page=reader.pages[page]
        text+=str(page.extract_text())
    return text

#Prompt Template

input_prompt="""
Hey Act Like a skilled or very experience ATS(Application Tracking System)
with a deep understanding of tech field,software engineering,data science ,data analyst
and big data engineer. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide 
best assistance for improving thr resumes. Assign the percentage Matching based 
on Jd and
the missing keywords with high accuracy
resume:{text}
description:{jd}
I want the response in one single string having the structure and also dont forget to give meanigfull response if 
ATS score is low give appropriate decision about Can apply also dont forget to give bullet points for improvement
**ATS Score**: "%",
  **MissingKeyword"**: [],\n
  **Can Select**: ""
"""
##MySQL Connector
con = c.connect(
    host="localhost",
    user="root",
    password="Kajal@123",
    database="ATS_resume"
)
## streamlit app




with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>',unsafe_allow_html=True)



st.title(':rainbow[RESUME GUARDIAN] ')
st.text("Improve Your Resume where ATS Efficiency Meets Accuracy: Unveiling LLM-Based ATS Resume Scoring Technology")
first_name = st.text_input("Enter First Name:")

last_name = st.text_input("Enter Last Name:")

roleoptions = ["--Select--","Data Analyst","Data Scientist","Machine Learning Engineer","Data Engineer","Software Engineer","Full Stack Engineer"]
role = st.selectbox("Select a role: ",roleoptions)

options = ["--Select--","Fresher", "1-2 Years","2-3 Years","3-4 Years", "4-5 Years","5-6 Years","7-10 Years",]
experience = st.selectbox("Select an option:", options)


jd=st.text_area("Paste the Job Description")
uploaded_file=st.file_uploader("Upload Your Resume",type="pdf",help="Please uplaod the pdf")





submit = st.button("Submit")

if submit:
    if uploaded_file is not None:
        text=input_pdf_text(uploaded_file)
        response=get_gemini_repsonse(input_prompt)
        st.subheader(response)
        import re

        match = re.search(r"ATS Score\*\*: (\d+)%", response)
        if match:
            ats_score = match.group(1)
        else:
            ats_score = "Not Provided by ATS"  # More informative default value

        ats_score_int= int(ats_score)
        

        cursor = con.cursor()
        sql = "INSERT INTO ats_resume_info (_first_name,_last_name,_role,_score,_experience) VALUES (%s,%s,%s,%s,%s)"
        values = (first_name,last_name,role,ats_score_int,experience)
        cursor.execute(sql,values)
    
        con.commit()
        st.success("Data Updated",icon="✅")

    else: 
        st.subheader("Please Upload your Resume")
