from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

def main():
    previous_response_id = None

    print("Python Learning Assistant")
    print("Type 'exit' to quit the program.\n")

    while True:
        question = input("You: ").strip()
        if question.lower() == "exit":
            break
        if not question:
            print("Please enter a valid question.")
            continue

        try:
            request = {
                "model": OPENAI_MODEL,
                "instructions": (
                    "You are a patient python instructor. "
                    "Teach step by step with practical examples. "

                ),
                "input": question,
            }

            if previous_response_id is not None:

                request["previous_response_id"] = previous_response_id 

            response = client.responses.create(**request)

            print("\nAssistant:", response.output_text, "\n")
            previous_response_id = response.id

        except Exception as error:
            print("Request failed:", error)

if __name__ == "__main__":
    main()