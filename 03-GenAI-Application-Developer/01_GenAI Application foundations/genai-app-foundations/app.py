from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL

def generate_answer(question: str) -> str:
    """Generate an answer to the given question using OpenAI's API."""
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.responses.create(
        model=OPENAI_MODEL,
        instructions = (
            "You are a helpful GenAI Trainer."
            "Explain technical concepts clearly, "
            "Step by step, using practical examples." 

        ),
        input=question,
    )
    return response.output_text

def main() -> None:
    print("Welcome to the GenAI Application!")

    question = input("Please enter your question: ").strip()

    try:
        answer = generate_answer(question)
        print("\nAI Response:")
        print(answer)
    except Exception as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()