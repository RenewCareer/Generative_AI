"""Data contracts for the document processing pipeline."""

from typing import Any

from pydantic import BaseModel, Field


class ChunkRecord(BaseModel):
    """One retrievable unit, carrying everything needed to cite and filter it later."""

    chunk_id: str
    doc_id: str
    source: str
    source_type: str
    page_number: int | None = None
    chunk_index: int = Field(ge=0)
    strategy: str
    text: str = Field(min_length=1)
    char_count: int = Field(ge=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PipelineReport(BaseModel):
    files_processed: int = 0
    files_failed: list[str] = Field(default_factory=list)
    chunks: int = 0
    average_chunk_chars: float = 0.0
