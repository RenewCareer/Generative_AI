from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

def stream_answer(question: str) -> None:
    if not question:
        raise ValueError("Question cannot be empty.")

    stream = client.responses.create(
        model = OPENAI_MODEL,
        instructions = ("Explain technical topics clearly"),
        input = question,
        stream = True
    )
    for event in stream:
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)

    print()


if __name__ == "__main__":
    question = input("Enter your question: ")
    stream_answer(question)
