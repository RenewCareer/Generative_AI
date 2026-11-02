"""Shared building blocks for the GenAI Application Developer track.

Modules 01 and 02 teach the raw provider SDKs. From module 03 onwards the lessons
reuse this package, so each module can focus on its own topic.
"""

from genai_kit.config import COURSE_DATA, ROOT, Settings, get_settings
from genai_kit.embeddings import Embedder, HashingEmbedder, OpenAIEmbedder, get_embedder
from genai_kit.llm import (
    AnthropicClient,
    LLMClient,
    LLMResponse,
    MockClient,
    OpenAIClient,
    ToolCall,
    Usage,
    get_llm,
)
from genai_kit.retrieval import (
    BM25Index,
    Chunk,
    SearchHit,
    VectorIndex,
    format_context,
    load_course_chunks,
    load_course_docs,
    recursive_chunk,
    reciprocal_rank_fusion,
)

__all__ = [
    "AnthropicClient",
    "BM25Index",
    "COURSE_DATA",
    "Chunk",
    "Embedder",
    "HashingEmbedder",
    "LLMClient",
    "LLMResponse",
    "MockClient",
    "OpenAIClient",
    "OpenAIEmbedder",
    "ROOT",
    "SearchHit",
    "Settings",
    "ToolCall",
    "Usage",
    "VectorIndex",
    "format_context",
    "get_embedder",
    "get_llm",
    "get_settings",
    "load_course_chunks",
    "load_course_docs",
    "recursive_chunk",
    "reciprocal_rank_fusion",
]
