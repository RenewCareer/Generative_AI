from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

response = client.chat.completions.create(
    model=OPENAI_MODEL,
    messages=[
        {"role": "user", "content": "Explain what a vector database does."}
    ]
)

if response.usage:
    print("Input tokens: ", response.usage.input_tokens)
    print("Output tokens: ", response.usage.output_tokens)
    print("Total Tokens: ", response.usage.total_tokens)
