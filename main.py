import ollama

from app.utils.logger import app_logger

app_logger.debug("starting the main")

response = ollama.chat(
    model="mistral:latest",
    messages=[
        {
            "role": "user",
            "content": "Hello, give me a 2 lines joke about AI?",
        }
    ],
    # format="json",
    options={"num_ctx": 8192, "temperature": 1},
)

print(response)
