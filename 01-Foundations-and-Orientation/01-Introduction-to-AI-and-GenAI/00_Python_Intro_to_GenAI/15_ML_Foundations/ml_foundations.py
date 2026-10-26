# ============================================================
# TOPIC 15: Machine Learning Foundations
# ============================================================

import numpy as np
import pandas as pd

# ============================================================
# SECTION 1: What is Machine Learning?
# ============================================================

print("=" * 60)
print("MACHINE LEARNING FOUNDATIONS")
print("=" * 60)
print("""
What is Machine Learning (ML)?
  Machine Learning is the practice of teaching computers to learn
  patterns from data and make predictions or decisions — WITHOUT
  being explicitly programmed for every rule.

  Traditional programming:
    Data + Rules → Answers

  Machine Learning:
    Data + Answers → Rules (the model learns the rules itself!)

Why does ML matter for Data Science & GenAI?
  - Identify patterns in large datasets humans can't manually inspect
  - Make predictions on new, unseen data
  - Power recommendation systems, fraud detection, image recognition
  - GenAI models (like ChatGPT, Gemini) are trained using ML at a massive scale
""")

# ============================================================
# SECTION 2: Types of ML (Supervised vs Unsupervised vs More)
# ============================================================

print("--- Types of Machine Learning ---")
print("""
1. SUPERVISED LEARNING
   - You provide labeled data (input + correct output)
   - The model learns to map input → output
   - Examples:
       Regression  : Predict a number (salary, house price, temperature)
       Classification: Predict a category (spam/not spam, disease/no disease)

2. UNSUPERVISED LEARNING
   - No labels — the model finds hidden patterns by itself
   - Examples:
       Clustering     : Group similar customers together (K-Means)
       Dimensionality : Reduce data to fewer features (PCA)
       Anomaly Detection: Find unusual data points

3. SEMI-SUPERVISED LEARNING
   - Mix of labeled and unlabeled data
   - Useful when labeling data is expensive

4. REINFORCEMENT LEARNING
   - Agent learns by taking actions and receiving rewards or penalties
   - Used in game AI (AlphaGo), robotics, self-driving cars

5. SELF-SUPERVISED / GENERATIVE AI
   - The model creates its own labels from raw data
   - Used in LLMs (GPT, Claude) and image generation (Stable Diffusion)
""")

# ============================================================
# SECTION 3: ML vs AI vs GenAI
# ============================================================

print("--- ML vs AI vs GenAI ---")
print("""
  AI (Artificial Intelligence)
    └── The broadest concept: any machine that simulates intelligence.

    ML (Machine Learning)
      └── A subset of AI: learns from data.

        Deep Learning
          └── A subset of ML: uses neural networks with many layers.

            GenAI (Generative AI)
              └── A subset of Deep Learning: creates new content
                  (text, images, code, audio).

  In simple terms:
    AI       = making machines smart
    ML       = teaching machines using data
    Deep Learning = ML using multi-layer neural networks
    GenAI    = AI that generates new content (ChatGPT, DALL-E, Sora)
""")

# ============================================================
# SECTION 4: ML Workflow Overview
# ============================================================

print("--- The ML Workflow ---")
print("""
Step 1: DEFINE THE PROBLEM
  - What are you predicting? (target variable)
  - Is it regression or classification?
  - What data do you have?

Step 2: COLLECT AND PREPARE DATA
  - Gather raw data
  - Clean it (handle missing values, outliers)
  - Engineer features (create new useful columns)

Step 3: EXPLORE THE DATA (EDA)
  - Visualize distributions
  - Check correlations
  - Understand the patterns

Step 4: PREPARE FOR MODELING
  - Train/test split (keep some data to test the final model)
  - Scale features (normalize numeric data)
  - Encode categories (convert text to numbers)

Step 5: TRAIN THE MODEL
  - Choose an algorithm (Linear Regression, Random Forest, etc.)
  - Fit the model on training data
  - The model learns the patterns

Step 6: EVALUATE THE MODEL
  - Test on the held-out test data (the model has never seen this)
  - Measure accuracy, precision, recall, RMSE, etc.

Step 7: IMPROVE AND TUNE
  - Try different algorithms
  - Tune hyperparameters (settings of the algorithm)

Step 8: DEPLOY
  - Put the model into production so others can use it
  - Monitor performance over time
""")

# ============================================================
# SECTION 5: Hands-on Concept Demo
# ============================================================

print("--- Conceptual Demo: What Supervised Learning Looks Like ---")

# Imagine this dataset: hours studied → exam score
hours   = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
scores  = np.array([45, 52, 58, 65, 70, 76, 82, 85, 91, 96])

print("\nHours Studied vs Score:")
print(f"{'Hours':>8} | {'Score':>7}")
print("-" * 20)
for h, s in zip(hours, scores):
    print(f"{h:>8} | {s:>7}")

# The "model" here is a simple linear equation: score = m * hours + b
# We can calculate the slope (m) and intercept (b) manually:
m = np.polyfit(hours, scores, 1)   # [slope, intercept]
slope, intercept = m[0], m[1]

print(f"\nLearned equation: Score = {slope:.2f} × Hours + {intercept:.2f}")

# Prediction for new, unseen data
new_hours = [3.5, 7.5, 12]
print("\nPredictions for new students:")
for h in new_hours:
    predicted_score = slope * h + intercept
    print(f"  {h} hours → predicted score: {predicted_score:.1f}")

# How well does the model fit the training data?
predicted_train = slope * hours + intercept
errors = scores - predicted_train
mae = np.mean(np.abs(errors))
print(f"\nMean Absolute Error on training data: {mae:.2f}")
print("(How far off the model is on average, in score points)")

# Explain the workflow
print("""
What just happened:
  1. We had labeled data: (hours, score) pairs
  2. The model LEARNED the relationship (found the best line)
  3. Now we can PREDICT scores for new students
  4. We EVALUATED how good the model is using MAE

This is the essence of supervised learning!
In practice, we use sklearn instead of doing the math manually.
""")

print("--- End of ML Foundations ---")
