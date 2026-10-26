# ============================================================
# TOPIC 19: Python Skills for GenAI
# ============================================================
# Install: pip install pandas numpy scikit-learn

import numpy as np
import pandas as pd
import re
import math
from collections import Counter

# ============================================================
# SECTION 1: Working with Large Datasets (Efficiently)
# ============================================================

print("=" * 60)
print("PYTHON SKILLS FOR GENERATIVE AI")
print("=" * 60)

print("\n--- Working with Large Datasets ---")
print("""
In GenAI, you often work with large text corpora, embedding tables,
or high-dimensional feature arrays.

Key techniques:
  - Use NumPy arrays instead of Python lists for speed
  - Use generators instead of loading all data into memory at once
  - Use chunked reading with Pandas for very large CSV files
""")

# Generator: process items one at a time without loading all into RAM
def data_generator(n):
    """Yields records one at a time — memory efficient."""
    for i in range(n):
        yield {"id": i, "text": f"Sample document number {i}", "label": i % 2}

# Process 1 million records without storing them all at once
total = 0
class_counts = {0: 0, 1: 0}
for record in data_generator(1_000_000):
    class_counts[record["label"]] += 1
    total += 1

print(f"Processed {total:,} records using a generator (low memory usage).")
print(f"Class distribution: {class_counts}")

# Chunked reading for large CSVs
# In real use: pd.read_csv("huge_file.csv", chunksize=10000)
print("""
Chunked reading pattern (for files too large to fit in RAM):
  for chunk in pd.read_csv("big_file.csv", chunksize=10000):
      process(chunk)
""")

# ============================================================
# SECTION 2: Understanding Embeddings (Conceptual + Hands-on)
# ============================================================

print("--- Understanding Embeddings ---")
print("""
What are Embeddings?
  An embedding is a list of numbers (a vector) that represents
  a word, sentence, or document in a multi-dimensional space.

  - Words/sentences with similar meanings have SIMILAR vectors.
  - This is the core technology behind GenAI models.

  Example:
    "king"  → [0.82, 0.14, -0.31, 0.54, ...]  (300+ dimensions)
    "queen" → [0.79, 0.18, -0.28, 0.60, ...]  (similar to king!)
    "car"   → [0.02, -0.55, 0.80, -0.12, ...] (very different)

  Famous analogy from Word2Vec:
    king - man + woman ≈ queen   (vector arithmetic!)
""")

# Simulate simple 3D embeddings for illustration
embeddings = {
    "king":   np.array([0.82, 0.14, -0.31]),
    "queen":  np.array([0.79, 0.18, -0.28]),
    "man":    np.array([0.65, 0.05, -0.40]),
    "woman":  np.array([0.62, 0.09, -0.37]),
    "car":    np.array([0.02, -0.55, 0.80]),
    "truck":  np.array([0.05, -0.50, 0.77]),
}

def cosine_similarity(a, b):
    """Measure how similar two vectors are. 1=identical, 0=unrelated, -1=opposite."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

print("Cosine similarity between word pairs:")
pairs = [("king", "queen"), ("king", "car"), ("car", "truck"), ("man", "woman")]
for w1, w2 in pairs:
    sim = cosine_similarity(embeddings[w1], embeddings[w2])
    print(f"  {w1:8} ↔ {w2:8} : {sim:.3f}  {'← very similar' if sim > 0.9 else '← different'}")

# Word analogy: king - man + woman = ?
result = embeddings["king"] - embeddings["man"] + embeddings["woman"]
print("\nking - man + woman = ?")
for word, vec in embeddings.items():
    sim = cosine_similarity(result, vec)
    print(f"  {word}: {sim:.3f}")

# ============================================================
# SECTION 3: Text Preprocessing Basics
# ============================================================

print("\n--- Text Preprocessing ---")
print("""
Before feeding text into an AI model, we must clean it:
  1. Lowercase everything
  2. Remove punctuation and special characters
  3. Remove stopwords (common words like 'the', 'is', 'a')
  4. Stemming or Lemmatization (reduce words to their root)
""")

# Sample text corpus
texts = [
    "The quick brown fox jumps over the lazy dog!",
    "Machine Learning and AI are transforming the world.",
    "Python is a GREAT language for data science & GenAI.",
    "Deep Learning models require LARGE datasets to train.",
    "Natural Language Processing (NLP) is fun!!!",
]

# Step 1: Lowercase
def lowercase(text):
    return text.lower()

# Step 2: Remove punctuation and special characters
def remove_special(text):
    return re.sub(r"[^a-z0-9\s]", "", text)

# Step 3: Remove stopwords
STOPWORDS = {"the", "is", "a", "an", "and", "are", "to", "for",
             "of", "in", "it", "this", "that", "be", "with",
             "was", "on", "at", "by", "from", "or", "as"}

def remove_stopwords(tokens):
    return [w for w in tokens if w not in STOPWORDS]

# Step 4: Simple stemming (remove common suffixes)
def simple_stem(word):
    for suffix in ["ing", "tion", "ed", "er", "s"]:
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            return word[:-len(suffix)]
    return word

def preprocess(text):
    text = lowercase(text)
    text = remove_special(text)
    tokens = text.split()
    tokens = remove_stopwords(tokens)
    tokens = [simple_stem(w) for w in tokens]
    return tokens

print("Text preprocessing pipeline:")
for text in texts[:3]:
    tokens = preprocess(text)
    print(f"\n  Original : {text}")
    print(f"  Processed: {tokens}")

# ============================================================
# SECTION 4: Introduction to Tokenization
# ============================================================

print("\n--- Tokenization ---")
print("""
Tokenization = splitting text into pieces (tokens) that a model can process.

Types:
  1. Word tokenization   : "hello world" → ["hello", "world"]
  2. Character tokenization: "hi" → ["h", "i"]
  3. Subword tokenization : "playing" → ["play", "##ing"]
                             (used by BERT, GPT, and most LLMs)

Why subword?
  - Handles unknown words (rare words split into known pieces)
  - Vocabulary stays manageable
  - "unhappiness" → ["un", "happiness"] → ["un", "happi", "ness"]
""")

# Simple word tokenizer
def word_tokenize(text):
    text = re.sub(r"[^a-zA-Z0-9\s']", " ", text)
    return text.lower().split()

# Character n-gram tokenizer
def char_ngrams(text, n=3):
    text = text.lower().replace(" ", "_")
    return [text[i:i+n] for i in range(len(text) - n + 1)]

# Vocabulary building
all_tokens = []
for text in texts:
    all_tokens.extend(word_tokenize(text))

vocab = sorted(set(all_tokens))
word_to_id = {word: idx for idx, word in enumerate(vocab)}
id_to_word = {idx: word for word, idx in word_to_id.items()}

print(f"Vocabulary size: {len(vocab)}")
print(f"First 15 words: {vocab[:15]}")

# Convert text to token IDs (what models actually receive)
sample = "machine learning is great"
token_ids = [word_to_id.get(w, -1) for w in sample.split()]
print(f"\nText   : '{sample}'")
print(f"Token IDs: {token_ids}")
print(f"Decoded: {[id_to_word.get(i, '<UNK>') for i in token_ids]}")

# Word frequency analysis
freq = Counter(all_tokens)
print(f"\nTop 10 most common words:")
for word, count in freq.most_common(10):
    print(f"  '{word}': {count}")

# ============================================================
# SECTION 5: Bag of Words (BoW) — Simple Text Representation
# ============================================================

print("\n--- Bag of Words ---")
print("""
Bag of Words: represent a document as a vector of word counts.
  Ignores word order — just counts how often each word appears.
  This is the simplest way to convert text to numbers for ML.
""")

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

documents = [
    "I love machine learning",
    "machine learning is fun",
    "I love Python for machine learning",
    "deep learning is part of machine learning",
]

# CountVectorizer: raw word counts
cv = CountVectorizer()
bow_matrix = cv.fit_transform(documents)
bow_df = pd.DataFrame(bow_matrix.toarray(), columns=cv.get_feature_names_out())
print("Bag of Words matrix:")
print(bow_df.to_string())

# TF-IDF: words that are frequent in a doc but rare across docs get higher weight
print("\n--- TF-IDF (Term Frequency–Inverse Document Frequency) ---")
print("""
TF-IDF downweights common words (like 'is', 'the') across all documents
and upweights words that are specific to one document.
This gives more meaningful representations than raw counts.
""")
tfidf = TfidfVectorizer()
tfidf_matrix = tfidf.fit_transform(documents)
tfidf_df = pd.DataFrame(tfidf_matrix.toarray().round(3),
                         columns=tfidf.get_feature_names_out())
print("TF-IDF matrix:")
print(tfidf_df.to_string())

# ============================================================
# SECTION 6: Using Python with AI Libraries (Conceptual)
# ============================================================

print("\n--- Python Libraries for GenAI ---")
print("""
Key Python libraries in the GenAI ecosystem:

  Text & NLP:
    transformers    → Hugging Face: BERT, GPT-2, T5, LLaMA (pip install transformers)
    tokenizers      → Fast tokenization (same ecosystem)
    sentence-transformers → Sentence embeddings

  Deep Learning Frameworks:
    PyTorch         → Most research models (pip install torch)
    TensorFlow      → Google's framework (pip install tensorflow)
    Keras           → High-level API for TensorFlow

  GenAI APIs:
    anthropic       → Use Claude (pip install anthropic)
    openai          → Use GPT-4, DALL-E (pip install openai)
    google-generativeai → Use Gemini (pip install google-generativeai)

  Vector Databases (for storing embeddings):
    faiss-cpu       → Facebook AI similarity search
    chromadb        → Simple vector database
    pinecone-client → Cloud vector database

Quick example — calling an AI API (structure only):
""")

example_code = '''
import anthropic

client = anthropic.Anthropic(api_key="your-api-key")

message = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Explain machine learning in 2 sentences."}
    ]
)

print(message.content[0].text)
'''
print(example_code)

print("--- End of Python Skills for GenAI ---")
