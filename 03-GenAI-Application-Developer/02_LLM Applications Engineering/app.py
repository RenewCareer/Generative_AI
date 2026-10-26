from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-4.1-mini",
    instructions=(
        "You are a data science instructor."
        "Explain technical concepts clearly in simple language and with examples "
    ),
    input="What is a confusion matrix?",
)

print(response.output_text)
