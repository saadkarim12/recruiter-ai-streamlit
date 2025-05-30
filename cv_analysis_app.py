import streamlit as st
import pandas as pd
import os
import tempfile
from io import BytesIO
from docx import Document
from PyPDF2 import PdfReader
from openai import OpenAI
import re

# === Load API Key ===
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="AI Resume Screener", layout="wide")
st.title("📄 AI Resume Screener for DevOps Roles")
st.write("Upload CVs and paste your job description. OpenAI will analyze each CV for suitability.")

# === Upload CVs ===
uploaded_files = st.file_uploader("📎 Upload CVs (PDF or DOCX)", type=["pdf", "docx"], accept_multiple_files=True)

# === Job Description Input ===
job_description = st.text_area("📌 Paste Job Description", height=200)

# === Extract Text from Resume ===
def extract_text(file):
    if file.name.endswith(".pdf"):
        try:
            reader = PdfReader(file)
            return "\n".join([page.extract_text() or "" for page in reader.pages])
        except Exception as e:
            return f"❌ PDF error: {e}"

    elif file.name.endswith(".docx"):
        try:
            doc = Document(BytesIO(file.read()))
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            return f"❌ DOCX error: {e}"

    return ""

# === Send to OpenAI GPT ===
def analyze_cv(cv_text, jd_text):
    if not cv_text.strip():
        return "⚠️ No content extracted from CV."

    prompt = f"""
You are a recruiter. Evaluate the candidate's CV against the job description.

Respond exactly in this format:

Summary: <summary of candidate's experience>
Match: <how well they match the role>
Recommendation: <Yes or No + reason>

Job Description:
{jd_text}

Resume:
{cv_text}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # or "gpt-3.5-turbo"
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ OpenAI API Error: {e}"

# === Extract Structured Info from GPT Response ===
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

# === Analyze Button Logic ===
if st.button("🔍 Analyze CVs") and uploaded_files and job_description:
    results = []

    for file in uploaded_files:
        st.write(f"📄 Processing: {file.name}")

        file.seek(0)  # reset pointer in case it's reused
        cv_text = extract_text(file)

        if not cv_text.strip():
            st.warning(f"⚠️ No content extracted from {file.name}. Skipping.")
            continue

        ai_output = analyze_cv(cv_text, job_description)
        st.text_area(f"🧠 GPT Output: {file.name}", ai_output, height=200)

        parsed = parse_analysis(ai_output)
        parsed["File Name"] = file.name
        results.append(parsed)

    df = pd.DataFrame(results)[["File Name", "Summary", "Match", "Recommendation"]]
    st.success("✅ CV Analysis Complete")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", data=csv, file_name="cv_analysis_results.csv", mime="text/csv")

else:
    st.info("Upload CVs and paste a job description to begin.")
