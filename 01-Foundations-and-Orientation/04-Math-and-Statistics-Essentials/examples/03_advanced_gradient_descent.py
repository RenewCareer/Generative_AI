"""
Advanced example: linear regression trained from scratch with gradient
descent -- no scikit-learn, no black boxes.

Requires: numpy, matplotlib (see requirements.txt).

This is a toy version of the exact algorithm (in spirit -- real neural
networks add many layers and a much more complex loss surface, but the
core loop is identical) used to train every neural network, including the
LLMs you've been calling via API in earlier scripts. Watching the loss
curve go down on a problem simple enough to fully understand is one of
the highest-leverage 10 minutes in this entire curriculum.

Run it with:
    python 03_advanced_gradient_descent.py

Output: loss_curve.png (written next to this script)
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUTPUT_PATH = Path(__file__).parent / "loss_curve.png"
LINE_COLOR = "#2E5EAA"


def make_synthetic_data(n: int = 50, seed: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """Generate points roughly following y = 3x + 7, with a bit of noise --
    the 'true' relationship the model has to discover from data alone."""
    rng = np.random.default_rng(seed)
    x = rng.uniform(0, 10, size=n)
    noise = rng.normal(0, 2, size=n)
    y = 3 * x + 7 + noise
    return x, y


def mean_squared_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """The LOSS function: how wrong are the model's predictions, on average
    (squared so errors in both directions count, and big errors are
    penalized more than small ones)."""
    return float(np.mean((y_true - y_pred) ** 2))


def train_linear_regression(
    x: np.ndarray, y: np.ndarray, learning_rate: float = 0.02, epochs: int = 500
) -> tuple[float, float, list[float]]:
    """Fit y = w*x + b using gradient descent, from scratch.

    At every step:
      1. Predict y_hat = w*x + b with the CURRENT w, b.
      2. Measure how wrong that is (the loss).
      3. Compute the GRADIENT: the direction in which w and b would need
         to move to make the loss WORSE.
      4. Step w and b a small distance in the OPPOSITE direction (downhill).
      5. Repeat.
    """
    w, b = 0.0, 0.0  # start with a bad guess: a flat line at zero
    n = len(x)
    loss_history: list[float] = []

    for epoch in range(epochs):
        y_pred = w * x + b
        loss = mean_squared_error(y, y_pred)
        loss_history.append(loss)

        # Gradients of the MSE loss with respect to w and b (calculus,
        # worked out once by hand -- this is the only "derivative" math
        # in this whole script, and it's the same shape for every linear
        # model you'll ever fit).
        error = y_pred - y
        grad_w = (2 / n) * np.sum(error * x)
        grad_b = (2 / n) * np.sum(error)

        # The actual "descent" step: move opposite the gradient.
        w -= learning_rate * grad_w
        b -= learning_rate * grad_b

        if epoch % 100 == 0 or epoch == epochs - 1:
            print(f"  epoch {epoch:3d}:  loss={loss:8.3f}   w={w:.3f}  b={b:.3f}")

    return w, b, loss_history


def main() -> None:
    x, y = make_synthetic_data()

    print("=" * 70)
    print("Training linear regression with gradient descent")
    print("(true relationship used to generate the data: y = 3x + 7 + noise)")
    print("=" * 70)

    w, b, loss_history = train_linear_regression(x, y)

    print("\n" + "=" * 70)
    print("Result")
    print("=" * 70)
    print(f"Learned:  y = {w:.3f}*x + {b:.3f}")
    print(f"Target:   y = 3.000*x + 7.000")
    print(f"Initial loss: {loss_history[0]:.3f}  ->  Final loss: {loss_history[-1]:.3f}")

    # Plot the loss curve -- the single most-recognized chart shape in ML:
    # a downward curve that flattens out as training converges.
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=150)
    ax.plot(loss_history, color=LINE_COLOR, linewidth=2)
    ax.set_title("Training Loss over Epochs (Gradient Descent)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Mean Squared Error (loss)")
    ax.grid(axis="y", color="#DDDDDD", linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUTPUT_PATH)
    print(f"\nSaved loss curve to: {OUTPUT_PATH}")

    print("\n" + "=" * 70)
    print("Interpretation")
    print("=" * 70)
    print(
        "The loss starts high (the model's first guess, w=0, b=0, is bad)\n"
        "and decreases every epoch, flattening out as w and b converge close\n"
        "to the true values (3, 7). This 'steep drop then flatten' shape is\n"
        "the same shape you'd see training a neural network with millions or\n"
        "billions of parameters -- the mechanism (compute gradient, step\n"
        "opposite it, repeat) doesn't change, only the scale."
    )


if __name__ == "__main__":
    main()
