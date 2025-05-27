import streamlit as st

st.set_page_config(page_title="Recruiter AI Job Form", layout="centered")
st.title("🚀 Recruiter AI Agent - Job Input Form")

# === Basic Job Info ===
st.header("📌 Job Information")

job_title = st.text_input("Job Title", placeholder="e.g., Senior DevOps Engineer")
experience = st.number_input("Minimum Years of Experience", min_value=0, max_value=50, value=3)
job_type = st.selectbox("Job Type", ["Remote", "Hybrid", "Onsite"])
location = st.text_input("Location", placeholder="City, Country")
requirements = st.text_area("Job Requirements", height=150, placeholder="List role responsibilities, education, certifications, etc.")
skills = st.text_area("Required Skills (comma-separated)", height=100, placeholder="e.g., Azure, Terraform, GitHub Actions")

# === Screening Questions ===
st.header("🧠 Screening Questions")

question_1 = st.text_input("Screening Question 1", placeholder="e.g., How many years of experience do you have with Azure?")
answer_1 = st.text_input("Acceptable Answer 1", placeholder="e.g., 3+")

question_2 = st.text_input("Screening Question 2", placeholder="e.g., Are you comfortable working remotely?")
answer_2 = st.text_input("Acceptable Answer 2", placeholder="e.g., Yes")

# === Submit Button ===
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
    st.markdown("### 🗂️ Final Job Data")
    st.json(job_data)
