from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1/",
    # required but ignored
    api_key="ollama",
)

prompts = [
    {
        "name": "payment_transaction",
        "description": "Prompt to answer queries specifically related to payments and transactions.",
        "prompt": """

""",
    },
    {
        "name": "funny_friendly_ai",
        "description": "Generic prompt to answer queries about anything and everything.",
    },
]

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
    model="llama2",
)
