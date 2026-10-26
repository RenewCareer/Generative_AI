import os
from anthropic import Anthropic

client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),  # This is the default and can be omitted
)

message = client.messages.create(
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Explain to me the Supervised Machine Learnign as to a little child with an example.",
        }
    ],
    model="claude-opus-5-5",
)
print(message.content)