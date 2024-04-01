import ollama
import json
from typing import List


from app.integrations import zendesk
from app.utils.logger import app_logger


def zendesk_solved_classifier():
    # client = OpenAI(
    #     base_url="http://localhost:11434/v1/",
    #     # required but ignored
    #     api_key="ollama",
    # )

    tickets = zendesk.get_tickets()
    app_logger.info(f"Classifying {len(tickets)} Tickets")
    solved: List[int] = []

    for ticket in tickets:
        ticket.comments = ticket.comments[-4:]

        classifier_prompt = """
You are a zendesk tickets classifier who tells whether a ticket has been solved or not based on the comments between a company's support team and their customer.
A ticket is considered solved if the customer has confirmed that the provided solution has fixed their issue.
If the author_id of the comment is same as requester_id then it is customer comment otherwise it's a MM support team comment.

# YOU MUST FOLLOW THESE INSTRUCTIONS CAREFULLY
<instructions>
- Classify, whether the provided ticket has been solved or not based on the comments.
- Once you classify the ticket, you must respond in the JSON format matching the following schema:
{
    "ticket": {
        "status": "<if solved then true else false>"
    }
}
- You respond only in JSON.
- Do not provide any additional notes or explanations.
</instructions>
"""
        chat_messages = [
            {"role": "system", "content": classifier_prompt},
            {
                "role": "user",
                "content": f"#ZENDESK TICKET JSON\n{ticket.model_dump_json()}",
            },
        ]

        # Ollama
        response = ollama.chat(
            model="mistral:latest",
            messages=chat_messages,
            format="json",
            options={"num_ctx": 8192, "temperature": 0},
        )["message"]["content"]

        # Open AI
        # response = (
        #     client.chat.completions.create(
        #         messages=chat_messages,
        #         model="mistral:latest",
        #         temperature=0,
        #         response_format={"type": "json_object"},
        #     )
        #     .choices[0]
        #     .message.content
        # )

        # print(
        #     f"Response for the ticket: {ticket.id} is:\n{response.choices[0].message.content}"
        # )
        try:
            is_solved = json.loads(response)["ticket"]["status"]
            if is_solved:
                solved.append(ticket.id)
        except:
            app_logger.warning(
                f"Response parsing failed for ticket: {ticket.id}: {response}"
            )

    print("Got DATA...")
    print(solved)


zendesk_solved_classifier()
