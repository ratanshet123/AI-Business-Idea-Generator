import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# ✅ Load model from local path
MODEL_PATH = "D:/Major project/models/all-MiniLM-L6-v2"  # Adjust this path if needed
model = SentenceTransformer(MODEL_PATH)

dimension = 384  # `all-MiniLM-L6-v2` generates 384-dimensional vectors
index = faiss.IndexFlatL2(dimension)

def store_idea(idea):
    """
    Converts a business idea into an embedding and stores it in FAISS.
    """
    vec = model.encode([idea])[0].astype("float32")  # ✅ Generate real embedding
    index.add(np.array([vec]))
    return "Idea stored in FAISS!"

def search_ideas(query):
    """
    Searches for similar business ideas in FAISS using embeddings.
    """
    vec = model.encode([query])[0].astype("float32")  # ✅ Embed the query
    _, indices = index.search(np.array([vec]), k=5)  # ✅ Find top 5 matches
    return indices.tolist()  # Convert to Python list for readability
