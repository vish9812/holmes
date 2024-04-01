import ollama

from app.integrations import zendesk
from app.utils import paths
from app.utils.logger import app_logger


_data_path = paths.get_path(paths.get_root_dir(), "data", "processed", "zendesk")


def generate_kb():
    solved_tickets = []
    tickets = [t for t in zendesk.get_tickets() if t.id in solved_tickets]

    app_logger.info(f"Generating KB articles for {len(tickets)} tickets.")

    for ticket in tickets:
        kb_prompt = """
        You are a Knowledge Base(KB) article writer.
        You are given a zendesk ticket in the JSON format with comments exchanged between Mattermost support team and their customer.
        You must find a problem statement and a solution from the ticket comments.
        
        # YOU MUST FOLLOW THESE INSTRUCTIONS CAREFULLY
        <instructions>
        - Identify a problem and a solution based on the comments.
        - Once you identify the problem, you must write a KB article in the MARKDOWN format.
        - A KB article must have a Problem statement and a Solution for it.
        - You respond only in MARKDOWN.
        - Do not provide any additional notes or explanations.
        </instructions>
        """

        chat_messages = [
            {"role": "system", "content": kb_prompt},
            {
                "role": "user",
                "content": f"#KB ARTICLE\n{ticket.model_dump_json()}",
            },
        ]

        # Ollama
        response = ollama.chat(
            model="mistral:latest",
            messages=chat_messages,
            options={"num_ctx": 8192, "temperature": 0.4},
        )["message"]["content"]

        file_path = paths.get_path(_data_path, f"{ticket.id}-kb.md")
        with open(file_path, "w") as file:
            file.write(response)


generate_kb()
