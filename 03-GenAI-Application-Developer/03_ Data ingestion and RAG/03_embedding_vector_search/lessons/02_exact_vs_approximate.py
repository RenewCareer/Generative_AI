"""Lesson 2: exact search against approximate indexes (ANN), measured on this machine.

Compares FAISS Flat (exact), IVF (clusters) and HNSW (graph) for build time, query speed,
recall and memory, on synthetic clustered vectors. Your numbers will differ by hardware.

Run: python lessons/02_exact_vs_approximate.py
"""

import time

import faiss
import numpy as np

DIMENSIONS = 128
VECTORS = 50_000
QUERIES = 200
K = 10


def make_vectors(count: int, dimensions: int, clusters: int = 200, seed: int = 0) -> np.ndarray:
    """Clustered vectors. Topics are fixed, so queries come from the same 'topics' as the data."""
    centres = np.random.default_rng(42).normal(size=(clusters, dimensions))
    rng = np.random.default_rng(seed)
    data = centres[rng.integers(0, clusters, count)] + rng.normal(scale=0.08, size=(count, dimensions))
    data = data.astype(np.float32)
    faiss.normalize_L2(data)
    return data


def recall_at_k(found: np.ndarray, truth: np.ndarray) -> float:
    """Of the true top-k neighbours, what share did the index return?"""
    return float(np.mean([len(set(a) & set(b)) / len(b) for a, b in zip(found, truth)]))


def evaluate(name: str, index, data: np.ndarray, queries: np.ndarray, truth: np.ndarray | None) -> np.ndarray:
    start = time.perf_counter()
    if not index.is_trained:
        index.train(data)
    index.add(data)
    build_s = time.perf_counter() - start

    start = time.perf_counter()
    _, found = index.search(queries, K)
    query_ms = (time.perf_counter() - start) / len(queries) * 1000

    recall = 1.0 if truth is None else recall_at_k(found, truth)
    memory_mb = faiss.serialize_index(index).nbytes / 1e6
    print(f"{name:<22}{build_s:>9.2f}s{query_ms:>11.3f}ms{recall:>10.1%}{memory_mb:>10.0f} MB")
    return found


def main() -> None:
    data = make_vectors(VECTORS, DIMENSIONS)
    queries = make_vectors(QUERIES, DIMENSIONS, seed=1)
    print(f"{VECTORS:,} vectors, {DIMENSIONS} dimensions, top-{K}\n")
    print(f"{'index':<22}{'build':>10}{'per query':>13}{'recall':>10}{'memory':>13}")

    truth = evaluate("Flat (exact)", faiss.IndexFlatIP(DIMENSIONS), data, queries, None)

    for nprobe in (1, 10):
        quantizer = faiss.IndexFlatIP(DIMENSIONS)
        ivf = faiss.IndexIVFFlat(quantizer, DIMENSIONS, 200, faiss.METRIC_INNER_PRODUCT)
        ivf.nprobe = nprobe
        evaluate(f"IVF nprobe={nprobe}", ivf, data, queries, truth)

    for ef_search in (16, 64):
        hnsw = faiss.IndexHNSWFlat(DIMENSIONS, 32, faiss.METRIC_INNER_PRODUCT)
        hnsw.hnsw.efSearch = ef_search
        evaluate(f"HNSW efSearch={ef_search}", hnsw, data, queries, truth)

    print("\nTakeaway: ANN indexes trade a little recall for much faster queries, and you tune")
    print("that trade-off with nprobe or efSearch. Below ~100k vectors, exact is often fine.")


if __name__ == "__main__":
    main()
