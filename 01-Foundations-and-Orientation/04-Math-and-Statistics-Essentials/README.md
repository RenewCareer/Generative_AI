# 1.4 Math and Statistics Essentials

## Why this matters

You don't need a math degree to work in GenAI, but three specific ideas — vectors/similarity, probability distributions, and gradient descent — explain *why* embeddings work, *why* a model's output feels "creative" or "deterministic," and *how* a model learns in the first place. Without this, RAG (Track 3) is a black box you copy-paste, and "temperature" is a magic knob instead of a concept you understand. This lesson builds all three from scratch in plain code, using nothing beyond what sub-topic 1.3 already gave you.

## Concepts

### 1. Vectors, dot product, and cosine similarity

An embedding is just a list of numbers (a vector) that represents the "meaning" of a piece of text, positioned in a high-dimensional space such that similar meanings end up close together. "Close together" is measured mathematically — most commonly with **cosine similarity**, which measures the angle between two vectors (not their length): 1.0 means pointing the same direction (very similar meaning), 0 means unrelated, -1 means opposite. You already previewed this in sub-topic 1.3 — this lesson makes it rigorous and builds it from raw math instead of trusting a library.

### 2. Probability distributions and softmax

When an LLM predicts "the next token," it doesn't output one answer — it outputs a score for *every possible token in its vocabulary*. The **softmax function** converts those raw scores ("logits") into a valid probability distribution (all values between 0 and 1, summing to 1). **Temperature** is a single number that reshapes that distribution before sampling: low temperature sharpens it toward the highest-scoring token (more deterministic, "safe" output), high temperature flattens it (more random, "creative" output). This is the actual mechanism behind a setting you've probably already seen in an AI product's UI.

### 3. Gradient descent — how a model learns

Training a model means adjusting its internal numbers (parameters) to reduce a **loss function** — a number that measures "how wrong" the model's predictions are. **Gradient descent** is the algorithm: compute the gradient (the direction of steepest increase of the loss), then step the parameters slightly in the *opposite* direction, repeat. Every neural network — from a tiny linear regression to a frontier LLM — is trained with a variant of this one idea. You'll implement it from scratch on a toy problem to build real intuition, not just recite the name.

## Step-by-step walkthrough

> 💡 **Prefer Jupyter?** Every script below also has a `.ipynb` notebook of the same name in `examples/`, with the explanation broken into markdown cells between runnable code cells, already executed and saved — including the loss-curve chart from step 5 — so you can read the notebooks before installing anything. Open with `jupyter notebook` / `jupyter lab`, or directly in VS Code / Cursor with the Jupyter extension.

1. **Read the three concepts above until you can restate each one in your own words**, out loud, without looking. This is the "explain it back" checkpoint from the Track 1 README — do it now, before code.
2. **Install dependencies:**
   ```bash
   cd 01-Foundations-and-Orientation/04-Math-and-Statistics-Essentials/examples
   pip install -r requirements.txt
   ```
3. **Run `01_beginner_vectors_similarity.py`.** It implements dot product, vector magnitude, and cosine similarity *both* by hand (pure Python loops) and with NumPy, and shows they produce identical results — proving NumPy isn't magic, just fast, correct implementations of the same math.
4. **Run `02_intermediate_probability_softmax.py`.** It implements softmax from scratch, then shows how changing "temperature" reshapes a probability distribution over a small fake vocabulary — you'll see the exact same probabilities an LLM would be sampling from, just over 5 toy tokens instead of 100,000+ real ones.
5. **Run `03_advanced_gradient_descent.py`.** It implements linear regression trained via gradient descent from scratch (no scikit-learn), on a small synthetic dataset, and plots the loss decreasing over training iterations — the single most important chart shape in all of machine learning. Output is saved as a PNG you can open and inspect.

### Try it yourself

- In script 1, add a third example pair of vectors that are *orthogonal* (cosine similarity ≈ 0) and confirm the script reports that correctly.
- In script 2, try temperature values of `0.1`, `1.0`, and `5.0` on the same logits and describe in your own words what changes about the resulting distribution at each extreme.
- In script 3, change the learning rate (the step size in gradient descent) to something too large (e.g. `1.0`) and observe what happens to the loss curve. This is your first hands-on encounter with a *diverging* training run — a real and common failure mode in ML.

## Sub-topic recap

You should now be able to compute cosine similarity by hand, explain what softmax and temperature actually do to a probability distribution, and explain gradient descent as "compute the slope, step opposite it, repeat" — all without treating any of these as a black box.

---
⬅️ Back to [Track 1 overview](../README.md)
