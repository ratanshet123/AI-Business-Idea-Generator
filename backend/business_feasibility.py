import json
import matplotlib.pyplot as plt
import numpy as np
from backend.llm import generate_ai_insights, ai_find_competitors

def generate_ai_competitors(business_idea, industry):
    """Fetches AI-generated competitors in plain text format."""
    competitors_text = ai_find_competitors(business_idea, industry)

    if not competitors_text:
        return "No competitors found."

    return competitors_text  # ✅ Competitor details returned as plain text

def generate_ai_financials(business_idea, budget):
    """Generates AI financial estimates."""
    financial_data = generate_ai_insights(business_idea, "Financials", budget, "None")

    # try:
    return financial_data  # ✅ Ensure valid JSON format
    # except json.JSONDecodeError:
    #     return {
    #         "Startup Cost": f"${budget}",
    #         "Profitability Margin": "10%",
    #         "Break-even Point": "12 months"
    #     }

def create_score_chart(scores):
    """Generates a feasibility score chart."""
    plt.figure(figsize=(6, 4))
    plt.barh(list(scores.keys()), list(scores.values()), color=['#1f77b4', '#ff7f0e', '#2ca02c'])
    plt.xlabel("Rating (1-10)")
    plt.xlim(0, 10)
    plt.title("Feasibility Ratings")
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.close()  # ✅ Prevents Streamlit from displaying duplicate charts
    return plt

def evaluate_business_feasibility(business_idea, industry, budget):
    """Runs feasibility analysis and generates a report."""
    competitors = generate_ai_competitors(business_idea, industry)
    financials = generate_ai_financials(business_idea, budget)
    insights = generate_ai_insights(business_idea, "Market Feasibility", budget, "None")

    report = f"📊 Feasibility Analysis for {business_idea} in {industry}\n\n"
    # report += f"💰 **Startup Cost:** {financials['Startup Cost']}\n"
    # report += f"📈 **Profitability:** {financials['Profitability Margin']}\n"
    # report += f"⏳ **Break-even Point:** {financials['Break-even Point']}\n"

    report += f"\n🔍 Insights:\n{insights}\n"
    report += "\n🏆 Financial Data:\n" + financials + "\n"
    report += "\n🏆 Top Competitors:\n" + competitors + "\n"

    return report
