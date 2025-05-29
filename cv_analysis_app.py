import streamlit as st
import pandas as pd
import os
import tempfile
from docx import Document
from PyPDF2 import PdfReader
from openai import OpenAI
import re

# === Setup OpenAI ===
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# === App Title ===
st.title("📄 AI Resume Screener - DevOps Role")

st.write("Upload PDF/DOCX CVs and paste your job description. OpenAI will analyze and rank candidates.")

# === Upload Files ===
uploaded_files = st.file_uploader("📎 Upload CVs (PDF or DOCX)", type=["pdf", "docx"], accept_multiple_files=True)

# === Job Description ===
job_description = st.text_area("📌 Job Description", height=200)

# === Extract Text ===
def extract_text(file):
    if file.name.endswith(".pdf"):
        reader = PdfReader(file)
        return "\n".join([page.extract_text() or "" for page in reader.pages])
    elif file.name.endswith(".docx"):
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    return ""

# === Force GPT Structured Output ===
def analyze_cv(cv_text, jd_text):
    if not cv_text.strip():
        return "⚠️ No content extracted from CV."

    prompt = f"""
You are a technical recruiter. Compare the candidate's resume to the job description.

Follow this format exactly:

Summary: <short summary of experience>

Match: <how well they meet requirements>

Recommendation: <Yes or No + one-line reason>

Job Description:
{jd_text}

Candidate Resume:
{cv_text}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # or "gpt-3.5-turbo"
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        print("✅ RAW GPT response:", response)
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"❌ OpenAI API Error: {e}"

# === Extract Fields from GPT Output ===
def parse_analysis(text):
    summary = re.search(r"(?i)summary[:\-]?\s*(.+)", text)
    match = re.search(r"(?i)match[:\-]?\s*(.+)", text)
    rec = re.search(r"(?i)recommendation[:\-]?\s*(.+)", text)
    return {
        "Summary": summary.group(1).strip() if summary else "N/A",
        "Match": match.group(1).strip() if match else "N/A",
        "Recommendation": rec.group(1).strip() if rec else "N/A",
        "GPT Response": text
    }

# === Analyze Button ===
if st.button("🔍 Analyze CVs") and uploaded_files and job_description:
    results = []

    for file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file.read())
            tmp_path = tmp.name

        st.write(f"📄 Processing: {file.name}")
        cv_text = extract_text(open(tmp_path, "rb"))
        response = analyze_cv(cv_text, job_description)
        st.text_area(f"🧠 GPT Output ({file.name})", value=response, height=200)

        parsed = parse_analysis(response)
        parsed["File Name"] = file.name
        results.append(parsed)

    df = pd.DataFrame(results)[["File Name", "GPT Response"]]
    st.success("✅ Analysis complete.")
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", data=csv, file_name="cv_analysis_results.csv", mime="text/csv")
else:
    st.info("Please upload CVs and provide a job description to begin.")
