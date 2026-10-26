# ============================================================
# TOPIC 20: Next Steps Toward GenAI
# ============================================================

import numpy as np
import math

# ============================================================
# SECTION 1: Introduction to Deep Learning Concepts
# ============================================================

print("=" * 60)
print("NEXT STEPS TOWARD GENERATIVE AI")
print("=" * 60)

print("""
--- What is Deep Learning? ---

Deep Learning = Machine Learning using Neural Networks with MANY layers.

  Input Layer → [Hidden Layer 1] → [Hidden Layer 2] → ... → Output Layer

Why "deep"?  Because of many hidden layers stacked on top of each other.

Classic ML vs Deep Learning:
  Classic ML  : You manually engineer features, then feed to model
  Deep Learning: The model LEARNS features automatically from raw data

Deep Learning excels at:
  - Images (CNNs — Convolutional Neural Networks)
  - Text and language (RNNs, Transformers)
  - Audio and speech
  - Video and multimodal inputs
""")

# ============================================================
# SECTION 2: How a Single Neuron Works (the Building Block)
# ============================================================

print("--- How a Neuron Works ---")
print("""
A single neuron:
  1. Takes multiple inputs (x1, x2, x3...)
  2. Multiplies each by a weight (w1, w2, w3...)
  3. Adds a bias (b)
  4. Passes through an activation function → output

  output = activation( w1*x1 + w2*x2 + w3*x3 + b )

This is exactly what Linear Regression does — but with an activation function
and millions of neurons chained together!
""")

# Manual single neuron
def sigmoid(z):
    """Sigmoid activation: squashes output between 0 and 1."""
    return 1 / (1 + math.exp(-z))

def relu(z):
    """ReLU activation: max(0, z) — most popular in hidden layers."""
    return max(0, z)

def neuron(inputs, weights, bias, activation="sigmoid"):
    """A single artificial neuron."""
    z = sum(w * x for w, x in zip(weights, inputs)) + bias
    if activation == "sigmoid":
        return sigmoid(z)
    elif activation == "relu":
        return relu(z)
    return z  # linear

# Example: predict if student passes (1) or fails (0)
# Inputs: [hours_studied, attendance_rate]
inputs  = [6.0, 0.85]
weights = [0.4, 0.6]
bias    = -0.5

output = neuron(inputs, weights, bias, activation="sigmoid")
print(f"Inputs  : hours_studied={inputs[0]}, attendance={inputs[1]}")
print(f"Weights : {weights}, Bias: {bias}")
print(f"Output  : {output:.4f}  → Prediction: {'Pass' if output >= 0.5 else 'Fail'}")

print("\nActivation functions demo:")
for z in [-3, -1, 0, 1, 3]:
    print(f"  z={z:3d} | sigmoid={sigmoid(z):.3f} | relu={relu(z):.1f}")

print("""
Common activation functions:
  Sigmoid : Output 0-1. Used for binary classification output.
  ReLU    : max(0,z). Most popular in hidden layers. Fast, effective.
  Tanh    : Output -1 to 1. Used in RNNs.
  Softmax : Converts to probabilities summing to 1. Used in multi-class output.
""")

# ============================================================
# SECTION 3: Understanding Transformers (High Level)
# ============================================================

print("--- Understanding Transformers ---")
print("""
The Transformer architecture (introduced in 2017) is the foundation of
ALL modern GenAI models: GPT, Claude, Gemini, BERT, T5, LLaMA, etc.

Before Transformers, we used RNNs which processed text word-by-word (slow).
Transformers process ALL words simultaneously using "Attention".

Key components:

1. TOKENIZATION
   Input text is broken into tokens (subwords).
   "Transformers are powerful" → ["Transform", "ers", "are", "power", "ful"]

2. EMBEDDINGS
   Each token is converted to a vector of numbers.

3. POSITIONAL ENCODING
   Since Transformers don't process in order, we add position info.
   Token at position 1 gets different encoding than position 5.

4. SELF-ATTENTION (the core innovation)
   Each word "looks at" all other words to understand context.
   "bank" in "river bank" vs "money bank" → different meaning from context.

   Attention computes: For each word, how much should I pay attention
   to every other word?

5. FEED-FORWARD LAYERS
   After attention, each token passes through a neural network.

6. STACKING
   Modern LLMs stack 96+ of these Transformer blocks on top of each other.
   GPT-4 has ~96 layers and ~1.8 trillion parameters!

7. OUTPUT
   For text generation: predicts the next most likely token.
   This is how ChatGPT, Claude, and Gemini generate text.
""")

# Simplified attention concept
print("Simplified Self-Attention Demo:")
print("""
  Sentence: "The cat sat on the mat"

  When processing "sat":
    Attention weights (how much to look at each word):
      "The"  : 0.05
      "cat"  : 0.40  ← high: the subject of sitting
      "sat"  : 0.15  ← itself
      "on"   : 0.20  ← preposition
      "the"  : 0.05
      "mat"  : 0.15  ← the location

  The model blends information from all words based on relevance.
  This context-awareness is what makes Transformers so powerful.
""")

# ============================================================
# SECTION 4: Python's Role in LLMs
# ============================================================

print("--- Python's Role in LLMs ---")
print("""
Python is the PRIMARY language for all LLM work:

  Training  : PyTorch / TensorFlow handle the math and GPU operations
  Fine-tuning: Hugging Face Transformers makes this accessible
  Inference : Call a model to generate text / embeddings
  Pipelines : LangChain, LlamaIndex for building AI applications
  Evaluation: Benchmarking and testing model outputs
  Deployment: FastAPI / Flask to serve models as APIs

The entire AI stack is Python:
  Data → Preprocessing (Pandas/NumPy) → Modeling (PyTorch) →
  Serving (FastAPI) → Monitoring (custom Python scripts)
""")

# ============================================================
# SECTION 5: Transition to TensorFlow / PyTorch (Preview)
# ============================================================

print("--- Preview: Deep Learning with PyTorch ---")

# Try to import torch; show the conceptual code if not available
try:
    import torch
    import torch.nn as nn

    print("PyTorch is installed!")

    # Simple neural network in PyTorch
    class SimpleNN(nn.Module):
        def __init__(self, input_size, hidden_size, output_size):
            super().__init__()
            self.fc1 = nn.Linear(input_size, hidden_size)
            self.relu = nn.ReLU()
            self.fc2 = nn.Linear(hidden_size, output_size)
            self.sigmoid = nn.Sigmoid()

        def forward(self, x):
            x = self.relu(self.fc1(x))
            return self.sigmoid(self.fc2(x))

    model = SimpleNN(input_size=4, hidden_size=8, output_size=1)
    print(f"\nSimple Neural Network:\n{model}")
    print(f"Total parameters: {sum(p.numel() for p in model.parameters())}")

except ImportError:
    print("PyTorch not installed. Install with: pip install torch")
    print("""
Conceptual PyTorch structure (what a neural net looks like):

  import torch
  import torch.nn as nn

  class SimpleNN(nn.Module):
      def __init__(self):
          super().__init__()
          self.fc1 = nn.Linear(4, 8)   # 4 inputs → 8 neurons
          self.relu = nn.ReLU()
          self.fc2 = nn.Linear(8, 1)   # 8 neurons → 1 output
          self.sigmoid = nn.Sigmoid()

      def forward(self, x):
          x = self.relu(self.fc1(x))   # Hidden layer
          return self.sigmoid(self.fc2(x))  # Output layer

  model = SimpleNN()
  optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
  loss_fn   = nn.BCELoss()

  # Training loop:
  for epoch in range(100):
      prediction = model(X_train)
      loss = loss_fn(prediction, y_train)
      optimizer.zero_grad()
      loss.backward()   # Backpropagation
      optimizer.step()  # Update weights
""")

# ============================================================
# SECTION 6: Using APIs for GenAI Applications
# ============================================================

print("\n--- Using GenAI APIs in Python ---")
print("""
You don't need to train your own model to build GenAI applications.
You can call powerful models through APIs:

  Anthropic (Claude):
    pip install anthropic

    from anthropic import Anthropic
    client = Anthropic(api_key="your-key")
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Summarize this text: ..."}]
    )
    print(response.content[0].text)

  OpenAI (GPT):
    pip install openai

    from openai import OpenAI
    client = OpenAI(api_key="your-key")
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print(response.choices[0].message.content)

  Common use cases you can build NOW:
    ✓ Summarization app (summarize long documents)
    ✓ Q&A bot over your own data
    ✓ Code review assistant
    ✓ Sentiment analysis tool
    ✓ Data extraction from unstructured text
    ✓ Image captioning (multimodal models)
""")

# ============================================================
# SECTION 7: Your Learning Roadmap
# ============================================================

print("=" * 60)
print("YOUR GENAI LEARNING ROADMAP")
print("=" * 60)
print("""
  COMPLETED (this course) ✓
  ┌─────────────────────────────────────────────────────┐
  │  Python Fundamentals → Data Structures → Functions   │
  │  NumPy → Pandas → EDA → Visualization                │
  │  Data Cleaning → ML Foundations → First ML Models    │
  │  Model Evaluation → Text Preprocessing → Embeddings  │
  └─────────────────────────────────────────────────────┘

  NEXT STEPS (recommended order):

  Step 1 — Strengthen Core ML
    → scikit-learn: Random Forest, XGBoost, SVM
    → Feature engineering
    → Hyperparameter tuning (GridSearchCV)
    → Kaggle competitions (practice!)

  Step 2 — Deep Learning Basics
    → Neural networks (PyTorch or TensorFlow/Keras)
    → CNNs for images
    → RNNs/LSTMs for sequences
    → Course: fast.ai or deeplearning.ai

  Step 3 — NLP and Transformers
    → Hugging Face Transformers library
    → Fine-tuning BERT for classification
    → Sequence-to-sequence models (T5, BART)
    → Course: Hugging Face NLP Course (free!)

  Step 4 — GenAI Applications
    → Calling LLM APIs (Anthropic, OpenAI, Gemini)
    → Prompt engineering
    → Retrieval-Augmented Generation (RAG)
    → LangChain / LlamaIndex

  Step 5 — Build & Deploy
    → FastAPI for serving models
    → Streamlit for rapid UI
    → Docker for packaging
    → Cloud deployment (AWS/GCP/Azure)

  Resources:
    - fast.ai: https://www.fast.ai/
    - Hugging Face: https://huggingface.co/learn
    - Kaggle: https://www.kaggle.com/learn
    - deeplearning.ai: https://www.deeplearning.ai/
    - Papers with Code: https://paperswithcode.com/
""")

print("Congratulations on completing Python for GenAI & Data Science!")
print("--- End of Topic 20 ---")
