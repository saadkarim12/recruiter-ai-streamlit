import streamlit as st
from openai import OpenAI
import os

# === CONFIG ===
st.set_page_config(page_title="Recruiter AI Job Form", layout="centered")

# Set OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or "your_openai_api_key_here")

# === TITLE ===
st.title("🚀 Recruiter AI Agent - Job Input & LinkedIn Post Generator")

# === INPUT FIELDS ===
st.header("📌 Job Information")

job_title = st.text_input("Job Title", placeholder="e.g., Senior DevOps Engineer")
experience = st.number_input("Minimum Years of Experience", min_value=0, max_value=50, value=3)
job_type = st.selectbox("Job Type", ["Remote", "Hybrid", "Onsite"])
location = st.text_input("Location", placeholder="City, Country")
requirements = st.text_area("Job Requirements", height=150, placeholder="Responsibilities, qualifications, etc.")
skills = st.text_area("Required Skills (comma-separated)", height=100, placeholder="e.g., Azure, Terraform, GitHub Actions")

# === SCREENING QUESTIONS ===
st.header("🧠 Screening Questions")

question_1 = st.text_input("Screening Question 1", placeholder="e.g., How many years of experience do you have with Azure?")
answer_1 = st.text_input("Acceptable Answer 1", placeholder="e.g., 3+")

question_2 = st.text_input("Screening Question 2", placeholder="e.g., Are you comfortable working remotely?")
answer_2 = st.text_input("Acceptable Answer 2", placeholder="e.g., Yes")

# === GPT FUNCTION ===
def generate_linkedin_post(job_data):
    skills_list = ", ".join(job_data["Skills"])
    screening_prompt = "\n".join(
        [f"- {q['question']} (Preferred: {q['answer']})"
         for q in job_data["Screening Questions"] if q["question"]]
    )

    prompt = f"""
Create a professional and engaging LinkedIn job post with the following details:

Job Title: {job_data['Job Title']}
Location: {job_data['Location']}
Job Type: {job_data['Job Type']}
Experience Required: {job_data['Experience']}+ years
Requirements: {job_data['Requirements']}
Skills: {skills_list}

Include these as screening questions:
{screening_prompt}

Tone: Friendly but professional. Format with headlines and bullet points. End with a call to action encouraging qualified candidates to apply.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a recruiter writing LinkedIn job posts."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content

# === SUBMIT BUTTON ===
if st.button("✅ Submit"):
    job_data = {
        "Job Title": job_title,
        "Experience": experience,
        "Job Type": job_type,
        "Location": location,
        "Requirements": requirements,
        "Skills": [skill.strip() for skill in skills.split(",")],
        "Screening Questions": [
            {"question": question_1, "answer": answer_1},
            {"question": question_2, "answer": answer_2}
        ]
    }

    st.success("🎉 Job input submitted successfully!")
    st.markdown("### 📋 Job Data Submitted")
    st.json(job_data)

    with st.spinner("⏳ Generating LinkedIn Job Post..."):
        linkedin_post = generate_linkedin_post(job_data)

    st.markdown("### 📢 LinkedIn Job Post")
    st.text_area("✅ Copy and paste your post to LinkedIn:", linkedin_post, height=300)
