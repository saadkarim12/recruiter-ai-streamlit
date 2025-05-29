import streamlit as st
import pandas as pd
import os
import tempfile
from docx import Document
from PyPDF2 import PdfReader
from openai import OpenAI
import re

# --- Load API Key ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- App UI ---
st.title("📄 AI Resume Screener - DevOps Role")
st.write("Upload CVs and paste the job description. The app will analyze each resume using OpenAI GPT.")

# --- Upload Files ---
uploaded_files = st.file_uploader("📎 Upload resumes (.pdf or .docx)", type=["pdf", "docx"], accept_multiple_files=True)

# --- Job Description ---
job_description = st.text_area("📌 Job Description", height=200)

# --- Text Extraction Function ---
def extract_text(file):
    if file.name.endswith(".pdf"):
        reader = PdfReader(file)
        return "\n".join([page.extract_text() or "" for page in reader.pages])
    elif file.name.endswith(".docx"):
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    return ""

# --- Parse GPT Response ---
def parse_analysis(text):
    summary = re.search(r"Summary:\s*(.+)", text, re.IGNORECASE)
    match = re.search(r"Match:\s*(.+)", text, re.IGNORECASE)
    rec = re.search(r"Recommendation:\s*(.+)", text, re.IGNORECASE)

    return {
        "Summary": summary.group(1).strip() if summary else "N/A",
        "Match": match.group(1).strip() if match else "N/A",
        "Recommendation": rec.group(1).strip() if rec else "N/A"
    }

# --- GPT Analysis Function ---
def analyze_cv(cv_text, jd_text):
    if not cv_text.strip():
        return "⚠️ No content extracted from CV."

    prompt = f"""
You are a technical recruiter. Assess the following candidate against the job description.

=== Job Description ===
{jd_text}

=== Candidate Resume ===
{cv_text}

Respond in this exact format:

Summary: <short summary of experience>

Match: <how well the candidate matches the qualifications>

Recommendation: <Yes/No + reason>
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # or gpt-3.5-turbo
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ OpenAI API Error: {e}"

# --- Button Logic ---
if st.button("🔍 Analyze CVs") and uploaded_files and job_description:
    results = []
    for file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file.read())
            tmp_path = tmp.name

        st.write(f"📄 Processing: {file.name}")
        cv_text = extract_text(open(tmp_path, "rb"))
        analysis = analyze_cv(cv_text, job_description)
        parsed = parse_analysis(analysis)
        parsed["File Name"] = file.name
        results.append(parsed)

    df = pd.DataFrame(results)
    st.success("✅ Analysis complete!")
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", data=csv, file_name="cv_analysis_results.csv", mime="text/csv")
else:
    st.info("Upload resumes and paste the JD to begin.")
