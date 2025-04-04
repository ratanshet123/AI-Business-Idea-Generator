import json
from langchain.chat_models import ChatOpenAI
from config import OPENROUTER_API_KEY

VALID_MODEL = "deepseek/deepseek-chat-v3-0324:free"

llm = ChatOpenAI(
    model_name=VALID_MODEL,
    openai_api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

def generate_business_idea(industry, budget, skills):
    """Uses AI to generate a business idea based on user inputs."""
    prompt = f"""
    Generate a unique business idea based on:
    - Industry: {industry}
    - Budget: ${budget}
    - Skills: {skills}

    Provide:
    - A brief summary of the idea.
    - Potential revenue model.
    - Target audience.
    
     Provide directly without asking any follow-up questions.
    """

    try:
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        return f"API Error: {e}"

def generate_ai_insights(business_idea, context, budget, skills):
    """Generates AI feasibility insights for the business idea."""
    prompt = f"""
    Based on the following business idea and context, provide insights:

    Business Idea: {business_idea}
    Context: {context}
    Budget: ${budget}
    Skills: {skills}
    
    Provide direct insights without asking any follow-up questions.
    """

    try:
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        return f"AI Insights Error: {e}"

def ai_find_competitors(business_idea, industry):
    """Fetches competitors as plain text with details, no structured format."""
    prompt = f"""
    List 5 existing companies competing with this business idea.

    Business Idea: {business_idea}
    Industry: {industry}

    Provide output in plain text format:
    Example Inc - A USA-based company with a capital of $10M and investments worth $50M.
    Startup XYZ - A European company with a capital of $5M and investments worth $20M.
    """

    try:
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        return "No competitors found."

def classify_business_category(business_idea):
    """Classifies a business idea into an industry category."""
    prompt = f"Classify this business idea into an industry: {business_idea}"

    try:
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        return "Unknown"
