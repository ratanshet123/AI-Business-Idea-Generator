import spacy

# Load English NLP model
nlp = spacy.load("en_core_web_sm")

def extract_keywords(text):
    """
    Extracts meaningful keywords (business type, industry, target audience)
    from the business idea for better search queries.
    """
    doc = nlp(text)

    # Extract important words (nouns & proper nouns)
    keywords = [token.text for token in doc if token.pos_ in ["NOUN", "PROPN"] and len(token.text) > 2]

    # Remove duplicate words & return top 5 keywords
    return list(set(keywords))[:5]
