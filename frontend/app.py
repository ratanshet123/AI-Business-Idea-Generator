import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import sys
import os
import json
import requests
import streamlit as st
import firebase_admin
from firebase_admin import auth, firestore, credentials
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter

# Firebase Setup
FIREBASE_WEB_API_KEY = "xxxxxxxxxxxxxxx"
if not firebase_admin._apps:
    cred = credentials.Certificate(r"D:\Major project\database\firebase-adminsdk.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Session State
st.session_state.setdefault("user", None)
st.session_state.setdefault("business_idea", None)
st.session_state.setdefault("industry", "")
st.session_state.setdefault("budget", 20000)
st.session_state.setdefault("skills", "")
st.session_state.setdefault("report", None)
st.session_state.setdefault("selected_idea_id", None)
st.session_state.setdefault("idea_page", 0)
st.session_state.setdefault("search_query", "")

# Authentication Functions
def sign_up(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        db.collection("users").document(user.uid).set({"email": email})
        return f"✅ User {email} created successfully!"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def sign_in(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, data=json.dumps(payload))
    data = response.json()
    if "idToken" in data:
        return {
            "status": "success",
            "idToken": data["idToken"],
            "email": data["email"],
            "localId": data["localId"]
        }
    else:
        return {
            "status": "error",
            "message": data.get("error", {}).get("message", "Unknown error")
        }

# Sidebar
with st.sidebar:
    st.header("🧑‍💼 Account")

    if not st.session_state["user"]:
        auth_choice = st.radio("Login or Signup", ["Login", "Signup"])
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if auth_choice == "Signup":
            if st.button("Create Account"):
                result = sign_up(email, password)
                if "successfully" in result:
                    st.success(result)
                else:
                    st.error(result)

        if auth_choice == "Login":
            if st.button("Login"):
                result = sign_in(email, password)
                if result["status"] == "success":
                    st.session_state["user"] = result["localId"]
                    st.success("✅ Logged in!")
                else:
                    st.error(f"⚠️ {result['message']}")

    else:
        if st.button("🚪 Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.divider()
        st.subheader("💬 Previous Ideas")
        st.text_input("🔍 Search", key="search_query")

        user_ref = db.collection("users").document(st.session_state["user"])
        ideas = list(user_ref.collection("ideas").stream())

        filtered_ideas = [doc for doc in ideas if st.session_state["search_query"].lower() in doc.to_dict().get("idea", "").lower()]
        ideas_per_page = 5
        start = st.session_state["idea_page"] * ideas_per_page
        end = start + ideas_per_page
        total_pages = (len(filtered_ideas) - 1) // ideas_per_page + 1

        for i, doc in enumerate(filtered_ideas[start:end]):
            idea_data = doc.to_dict()
            title = idea_data.get("idea", "")[:40] + "..."
            selected = st.session_state.get("selected_idea_id") == doc.id
            if st.button(f"{'👉' if selected else '💡'} {title}", key=f"idea_button_{doc.id}"):
                st.session_state.update({
                    "selected_idea_id": doc.id,
                    "business_idea": idea_data["idea"],
                    "industry": idea_data["industry"],
                    "budget": idea_data["budget"],
                    "skills": idea_data["skills"]
                })

        col1, col2 = st.columns(2)
        with col1:
            if st.session_state["idea_page"] > 0:
                if st.button("⬅️ Prev"):
                    st.session_state["idea_page"] -= 1
        with col2:
            if end < len(filtered_ideas):
                if st.button("Next ➡️"):
                    st.session_state["idea_page"] += 1

# Main App
st.title("🚀 AI-Powered Business Idea Generator")

if not st.session_state["user"]:
    st.warning("⚠️ Please login to continue.")
    st.stop()

industry = st.text_input("Enter Industry", value=st.session_state["industry"])
budget = st.number_input("Enter Your Budget ($)", min_value=1000, step=500, value=st.session_state["budget"])
skills = st.text_area("List Your Skills", value=st.session_state["skills"])

st.session_state.update({"industry": industry, "budget": budget, "skills": skills})

from backend.llm import generate_business_idea
from backend.business_feasibility import evaluate_business_feasibility

if st.button("Generate Idea"):
    if industry and budget and skills:
        idea = generate_business_idea(industry, budget, skills)
        st.session_state["business_idea"] = idea
        db.collection("users").document(st.session_state["user"]).collection("ideas").add({
            "industry": industry,
            "budget": budget,
            "skills": skills,
            "idea": idea
        })
        st.success("✅ Idea saved to your account!")
    else:
        st.warning("⚠️ Please fill in all fields.")

if st.session_state["business_idea"]:
    st.subheader("💡 Business Idea:")
    st.markdown(f"**{st.session_state['business_idea']}**")

if st.button("Check Feasibility"):
    if st.session_state["business_idea"]:
        with st.spinner("🔍 Analyzing Feasibility..."):
            report = evaluate_business_feasibility(st.session_state["business_idea"], industry, budget)
            st.session_state["report"] = report
            db.collection("users").document(st.session_state["user"]).collection("reports").document("latest").set({"report": report})

        st.subheader("📊 Feasibility Analysis Report:")
        st.markdown(report)
    else:
        st.warning("⚠️ Generate a business idea first.")

def generate_pdf(report_text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], fontSize=18, spaceAfter=12, alignment=TA_CENTER)
    section_style = ParagraphStyle("SectionStyle", parent=styles["Heading2"], fontSize=14, spaceBefore=12, spaceAfter=6)
    body_style = ParagraphStyle("BodyStyle", parent=styles["BodyText"], fontSize=12, spaceAfter=6)

    elements = [Paragraph("Business Feasibility Report", title_style), Spacer(1, 12)]

    sections = report_text.split("\n\n")
    for section in sections:
        section = section.strip()
        if section:
            if "**" in section:
                parts = section.split("**", 2)
                if len(parts) > 1:
                    title = parts[1].strip()
                    content = parts[2].strip() if len(parts) > 2 else ""
                    elements.append(Paragraph(f"<b>{title}</b>", section_style))
                    elements.append(Spacer(1, 4))
                    if content:
                        elements.append(Paragraph(content, body_style))
            else:
                elements.append(Paragraph(section, body_style))
            elements.append(Spacer(1, 8))

    doc.build(elements)
    buffer.seek(0)
    return buffer

if st.session_state["report"]:
    if st.button("Download Feasibility Report"):
        pdf_buffer = generate_pdf(st.session_state["report"])
        st.download_button("📥 Download PDF", pdf_buffer, file_name="Feasibility_Report.pdf", mime="application/pdf")
