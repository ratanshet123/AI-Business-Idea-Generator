# Business Feasibility Analysis Tool

A comprehensive tool for analyzing business ideas using AI-powered insights, market analysis, and feasibility scoring.

## Features
- AI-powered business insights using LLMs
- Competitor analysis and market research
- Firebase authentication and data storage
- Semantic search capabilities
- Streamlit web interface

## Prerequisites
- Python 3.8+
- Firebase project with credentials
- OpenRouter API key

## Installation
1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
export OPENROUTER_API_KEY="your_api_key"
export FIREBASE_CREDENTIALS_PATH="path/to/credentials.json"
```

## Project Structure
```
backend/          # Core business logic and AI integration
database/         # Firebase configuration and auth
frontend/         # Streamlit web interface
models/           # Local model storage
```

## Usage
1. Start the application:
```bash
streamlit run frontend/app.py
```

2. Access the web interface at `http://localhost:8501`

## Configuration
Edit `config.py` to set:
- OpenRouter API key
- Firebase credentials path

## Dependencies
- Streamlit
- Firebase Admin SDK
- Sentence Transformers
- FAISS
