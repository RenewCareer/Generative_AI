from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL
from schemas import ReviewAnalysis

client = OpenAI(api_key=OPENAI_API_KEY)


def analyze_review(review_text: str) -> ReviewAnalysis:
    if not review.strip():
        raise ValueError("Review text cannot be empty.")

    response = client.responses.parse(
        model=OPENAI_MODEL,
        instructions = (
            "Analyze the customer feedback for a business. "
            "Classify the sentiment based on the review"
            "Do not invent facts not present in the review. "
            "Return the results using the supplied schema. "
        ),
        input = review,
        text_format = ReviewAnalysis,
    )

    if response.output_parsed is None:
        raise ValueError(
            "The Models did not return a parsed review analysis."
        )

    return response.output_parsed

if __name__ == "__main__":
    review = input("Enter a customer review: ")
    try:
        result = analyze_review(review)

        print("\nStructured Analysis")
        print(f"Sentiment: {result.sentiment}")
        print(f"Category: {result.category}")
        print(f"Explanation: {result.explanation}")
        print(f"Recommended Action: {result.recommended_action}")

        print("\nJSON Output")
        print(result.model_dump_json(indent=2))

    except ValueError as error:
        print(f"Could not analyze review: {error}")
    except Exception as error:
        print("API request failed:", error)
