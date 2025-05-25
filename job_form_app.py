import streamlit as st

st.title("Private Recruiter AI Agent - Job Form")

job_title = st.text_input("Job Title")
experience = st.number_input("Years of Experience", min_value=0, max_value=50)
job_type = st.selectbox("Job Type", ["Remote", "Hybrid", "Onsite"])
location = st.text_input("Location")
requirements = st.text_area("Job Requirements")
skills = st.text_area("Required Skills (comma-separated)")

if st.button("Submit"):
    job_data = {
        "Job Title": job_title,
        "Experience": experience,
        "Job Type": job_type,
        "Location": location,
        "Requirements": requirements,
        "Skills": [skill.strip() for skill in skills.split(",")]
    }
    st.success("Job data submitted successfully!")
    st.json(job_data)
