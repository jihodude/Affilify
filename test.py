import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def preprocess_text(text):
    doc = nlp(text.lower())
    tokens = [token.text for token in doc if token.is_alpha and not token.is_stop]
    return " ".join(tokens)

# Example usage
text = "A dog is happily playing in the park!"
cleaned_text = preprocess_text(text)
print("Cleaned Text:", cleaned_text)




















# from transformers import BertTokenizer, BertModel
# import torch
# from sklearn.metrics.pairwise import cosine_similarity
# from sentence_transformers import SentenceTransformer, util

# # Load SentenceTransformer model
# model = SentenceTransformer('all-MiniLM-L6-v2')

# # Function to calculate similarity
# def calculate_similarity(text1, text2):
#     # Generate embeddings for both texts
#     emb1 = model.encode(text1)
#     emb2 = model.encode(text2)
#     # Calculate cosine similarity
#     similarity = util.cos_sim(emb1, emb2)
#     return similarity.item()  # Convert tensor to scalar

# # Example usage
# query = "A dog playing in the park."
# video_caption = "A puppy running outdoors."
# similarity_score = calculate_similarity(query, video_caption)
# print("Cosine Similarity Score:", similarity_score)
