import sys

# Windows consoles often default to cp1252, which crashes on model output like
# "✓", "’" or emoji. Force UTF-8 for every script that imports ai_core.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure") and (_stream.encoding or "").lower() != "utf-8":
        _stream.reconfigure(encoding="utf-8", errors="replace")

from .assistant import Assistant, AssistantError, Reply, UsageTotals
from .config import MissingAPIKeyError, get_settings
from .jsonutil import extract_json
from .pricing import estimate_cost

__all__ = [
    "Assistant", "AssistantError", "Reply", "UsageTotals",
    "MissingAPIKeyError", "get_settings", "extract_json", "estimate_cost",
]
