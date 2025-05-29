import streamlit as st
import pandas as pd
import os
import tempfile
from docx import Document
from PyPDF2 import PdfReader
from openai import OpenAI
import re

# === Initialize OpenAI ===
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="AI CV Screener", layout="wide")
st.title("📄 AI Resume Screener – DevOps Role")

st.write("Upload CVs and paste the job description. This app will analyze each resume using GPT.")

# === Upload Files ===
uploaded_files = st.file_uploader("📎 Upload CVs (PDF or DOCX)", type=["pdf", "docx"], accept_multiple_files=True)

# === Job Description ===
job_description = st.text_area("📌 Paste the Job Description", height=200)

# === Extract Text Function ===
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

def extract_text(file):
    if file.name.endswith(".pdf"):
        # Try text extraction first
        reader = PdfReader(file)
        text = "\n".join([page.extract_text() or "" for page in reader.pages])
        if text.strip():
            return text

        # If no text, use OCR
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file.read())
                tmp_path = tmp.name

            images = convert_from_path(tmp_path)
            text = ""
            for image in images:
                text += pytesseract.image_to_string(image)
            return text

        except Exception as e:
            return f"❌ OCR failed: {e}"

    elif file.name.endswith(".docx"):
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs])

    return ""

# === OpenAI Analysis ===
def analyze_cv(cv_text, jd_text):
    if not cv_text.strip():
        return "⚠️ No content extracted from CV."

    prompt = f"""
You are a recruiter. Assess this candidate against the DevOps job description.

Respond EXACTLY in this format:

Summary: <summary of experience>
Match: <how they meet or miss job criteria>
Recommendation: <Yes or No + reason>

Job Description:
{jd_text}

Resume:
{cv_text}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # or use "gpt-3.5-turbo"
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ OpenAI API Error: {e}"

# === Parse Response ===
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

# === Run Analysis ===
if st.button("🔍 Analyze CVs") and uploaded_files and job_description:
    results = []

    for file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file.read())
            tmp_path = tmp.name

        st.write(f"📄 Processing: {file.name}")
        cv_text = extract_text(open(tmp_path, "rb"))
        gpt_output = analyze_cv(cv_text, job_description)

        st.text_area(f"🧠 GPT Output for {file.name}", gpt_output, height=200)

        parsed = parse_analysis(gpt_output)
        parsed["File Name"] = file.name
        results.append(parsed)

    df = pd.DataFrame(results)[["File Name", "Summary", "Match", "Recommendation"]]
    st.success("✅ CV Analysis Complete")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV Results", data=csv, file_name="cv_analysis_results.csv", mime="text/csv")
else:
    st.info("Upload CVs and enter a job description, then click Analyze.")
