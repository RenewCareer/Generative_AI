"""Lesson 3: streaming for perceived speed, and bounded memory for long conversations.

Run: python lessons/03_streaming_and_memory.py
"""

from genai_kit import get_llm


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


class ConversationMemory:
    """Keeps the newest turns that fit a token budget, always dropping whole exchanges."""

    def __init__(self, max_tokens: int = 200) -> None:
        self.max_tokens = max_tokens
        self.messages: list[dict[str, str]] = []
        self.dropped = 0

    def add(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})
        self._trim()

    def tokens(self) -> int:
        return sum(estimate_tokens(message["content"]) for message in self.messages)

    def _trim(self) -> None:
        # Keep at least the latest user message. Removing pairs keeps the roles alternating.
        while self.tokens() > self.max_tokens and len(self.messages) > 2:
            del self.messages[:2]
            self.dropped += 2


def main() -> None:
    llm = get_llm()

    print("STREAMING: the first words arrive quickly, even if the full answer takes seconds")
    for delta in llm.stream([{"role": "user", "content": "Explain streaming in one line."}]):
        print(delta, end="", flush=True)
    print("\n")

    print("MEMORY: each turn resends the history, so it must be bounded")
    memory = ConversationMemory(max_tokens=90)
    for number in range(1, 7):
        memory.add("user", f"Question number {number}, with a little extra context to take up some space.")
        memory.add("assistant", llm.complete(memory.messages, max_tokens=50).text)
        print(f"  turn {number}: {len(memory.messages)} messages, ~{memory.tokens()} tokens, dropped {memory.dropped}")

    print("\nThe oldest turns are forgotten. Production systems also summarise them or store")
    print("durable facts separately, then re-inject what is relevant.")


if __name__ == "__main__":
    main()
