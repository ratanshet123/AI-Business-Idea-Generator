import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import sys
import os
import streamlit as st
import firebase_admin
from firebase_admin import auth, firestore, credentials
from backend.llm import generate_business_idea
from backend.business_feasibility import evaluate_business_feasibility
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ✅ Firebase Initialization
if not firebase_admin._apps:
    cred = credentials.Certificate(r"D:\Major project\database\firebase-adminsdk.json")
    firebase_admin.initialize_app(cred)

# ✅ Firestore Database
db = firestore.client()

# ✅ Streamlit Session State Initialization
st.session_state.setdefault("user", None)
st.session_state.setdefault("business_idea", None)
st.session_state.setdefault("industry", "")
st.session_state.setdefault("budget", 20000)
st.session_state.setdefault("skills", "")
st.session_state.setdefault("report", None)

st.title("🚀 AI-Powered Business Idea Generator")

# -----------------------------------------
# 🔹 USER AUTHENTICATION (LOGIN / SIGNUP)
# -----------------------------------------
auth_choice = st.sidebar.radio("Login or Signup", ["Login", "Signup"])

email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("Password", type="password")

if auth_choice == "Signup":
    if st.sidebar.button("Create Account"):
        try:
            user = auth.create_user(email=email, password=password)
            db.collection("users").document(user.uid).set({"email": email})  # Save to Firestore
            st.sidebar.success("✅ Account created! Please login.")
        except Exception as e:
            st.sidebar.error(f"⚠️ {str(e)}")

if auth_choice == "Login":
    if st.sidebar.button("Login"):
        try:
            user = auth.get_user_by_email(email)
            st.session_state["user"] = user.uid
            st.sidebar.success("✅ Logged in!")
            
            # 🔥 Load the last feasibility report from Firestore
            user_ref = db.collection("users").document(user.uid)
            report_doc = user_ref.collection("reports").document("latest").get()
            if report_doc.exists:
                st.session_state["report"] = report_doc.to_dict()["report"]
        except Exception as e:
            st.sidebar.error("⚠️ Invalid login credentials.")

# If user is not logged in, stop execution
if not st.session_state["user"]:
    st.warning("⚠️ Please login to continue.")
    st.stop()

# -----------------------------------------
# 🔹 BUSINESS IDEA GENERATION
# -----------------------------------------
industry = st.text_input("Enter Industry", value=st.session_state["industry"])
budget = st.number_input("Enter Your Budget ($)", min_value=1000, step=500, value=st.session_state["budget"])
skills = st.text_area("List Your Skills", value=st.session_state["skills"])

# Store session state
st.session_state.update({"industry": industry, "budget": budget, "skills": skills})

if st.button("Generate Idea"):
    if industry and budget and skills:
        st.session_state["business_idea"] = generate_business_idea(industry, budget, skills)
        
        # ✅ Save to Firestore
        user_ref = db.collection("users").document(st.session_state["user"])
        ideas_ref = user_ref.collection("ideas").document()
        ideas_ref.set({
            "industry": industry,
            "budget": budget,
            "skills": skills,
            "idea": st.session_state["business_idea"]
        })
        
        st.success("✅ Idea saved to your account!")
    else:
        st.warning("⚠️ Please fill in all fields.")

if st.session_state["business_idea"]:
    st.subheader("💡 Business Idea:")
    st.markdown(f"**{st.session_state['business_idea']}**")

# -----------------------------------------
# 🔹 BUSINESS FEASIBILITY REPORT
# -----------------------------------------
if st.button("Check Feasibility"):
    if st.session_state["business_idea"]:
        with st.spinner("🔍 Analyzing Feasibility..."):
            report = evaluate_business_feasibility(st.session_state["business_idea"], industry, budget)
        
        st.subheader("📊 Feasibility Analysis Report:")
        st.markdown(report)

        # ✅ Store Report in Firestore
        user_ref = db.collection("users").document(st.session_state["user"])
        report_ref = user_ref.collection("reports").document("latest")
        report_ref.set({"report": report})
        
        # ✅ Store in session state to persist
        st.session_state["report"] = report
    else:
        st.warning("⚠️ Generate a business idea first.")

# -----------------------------------------
# 🔹 BUSINESS FEASIBILITY REPORT (FORMATTED PDF)
# -----------------------------------------
def generate_pdf(report_text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontSize=18,
        spaceAfter=12,
        alignment=TA_CENTER
    )

    section_style = ParagraphStyle(
        "SectionStyle",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=12,
        spaceAfter=6,
        textColor="black",
        bold=True
    )

    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["BodyText"],
        fontSize=12,
        spaceAfter=6
    )

    elements = []

    # ✅ Title
    elements.append(Paragraph("Business Feasibility Report", title_style))
    elements.append(Spacer(1, 12))

    # ✅ Process and Format Report Text
    sections = report_text.split("\n\n")  # Splitting paragraphs properly
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
            else:
                elements.append(Paragraph(section, body_style))

        elements.append(Spacer(1, 8))

    doc.build(elements)
    buffer.seek(0)
    return buffer

if st.session_state["report"]:
    if st.button("Download Feasibility Report"):
        pdf_buffer = generate_pdf(st.session_state["report"])
        st.download_button(
            "📥 Download PDF", 
            pdf_buffer, 
            file_name="Feasibility_Report.pdf", 
            mime="application/pdf"
        )
