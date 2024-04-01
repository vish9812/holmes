import json

from pandas import DataFrame

# Assuming we have the following data
data = {
    "transaction_id": ["T1001", "T1002", "T1003", "T1004", "T1005"],
    "customer_id": ["C001", "C002", "C003", "C002", "C001"],
    "payment_amount": [125.50, 89.99, 120.00, 54.30, 210.20],
    "payment_date": [
        "2021-10-05",
        "2021-10-06",
        "2021-10-07",
        "2021-10-05",
        "2021-10-08",
    ],
    "payment_status": ["Paid", "Unpaid", "Paid", "Paid", "Pending"],
}

# Create DataFrame
df_original = DataFrame(data)


def retrieve_payment_summary(df: DataFrame, transaction_id: str) -> str:
    if transaction_id in df.transaction_id.values:
        val = df[df.transaction_id == transaction_id]
        return json.dumps(
            {
                "summary": {
                    "status": val.payment_status.item(),
                    "amount": val.payment_amount.item(),
                    "date": val.payment_date.item(),
                }
            }
        )
    return json.dumps({"error": "transaction id not found."})


def retrieve_payment_status(df: DataFrame, transaction_id: str) -> str:
    if transaction_id in df.transaction_id.values:
        return json.dumps(
            {"status": df[df.transaction_id == transaction_id].payment_status.item()}
        )
    return json.dumps({"error": "transaction id not found."})


def retrieve_payment_date(df: data, transaction_id: str) -> str:
    if transaction_id in df.transaction_id.values:
        return json.dumps(
            {"date": df[df.transaction_id == transaction_id].payment_date.item()}
        )
    return json.dumps({"error": "transaction id not found."})


tools = [
    {
        "type": "function",
        "function": {
            "name": "retrieve_payment_status",
            "description": "Get payment status of a transaction",
            "parameters": {
                "type": "object",
                "properties": {
                    "transaction_id": {
                        "type": "string",
                        "description": "The transaction id.",
                    }
                },
                "required": ["transaction_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "retrieve_payment_date",
            "description": "Get payment date of a transaction",
            "parameters": {
                "type": "object",
                "properties": {
                    "transaction_id": {
                        "type": "string",
                        "description": "The transaction id.",
                    }
                },
                "required": ["transaction_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "retrieve_payment_summary",
            "description": "Get payment summary of a transaction",
            "parameters": {
                "type": "object",
                "properties": {
                    "transaction_id": {
                        "type": "string",
                        "description": "The transaction id.",
                    }
                },
                "required": ["transaction_id"],
            },
        },
    },
]

import functools

names_to_functions = {
    "retrieve_payment_status": functools.partial(
        retrieve_payment_status, df=df_original
    ),
    "retrieve_payment_date": functools.partial(retrieve_payment_date, df=df_original),
    "retrieve_payment_summary": functools.partial(
        retrieve_payment_summary, df=df_original
    ),
}

# tool_calls = {
#     "tool_calls": [
#         {"name": "", "arguments": {"transaction_id": "T1001"}}
#     ]
# }


from mistralai.models.chat_completion import ChatMessage

messages = [
    ChatMessage(
        role="system",
        content=f"""
You are an intelligent helpful funny colleague.
If the queries are related to payment transactions, you can access the following functions JSON schema. Otherwise respond normally:
# FUNCTIONS:

{json.dumps(tools)}

# YOU MUST FOLLOW THESE INSTRUCTIONS CAREFULLY FOR PAYMENT TRANSACTIONS RELATED QUERIES ONLY.
<instructions>
- Identify, if any, functions can be used to respond to the users payment transaction related query.
- If you identify the functions which can be used, you must respond in the JSON format matching the following schema:
{{
    "functions": [{{
    "name": "<name of the selected function>",
    "parameters": <parameters for the selected function, matching the function's JSON schema>
    }}]
}}
- Do not provide any additional notes or explanations.
</instructions>
""",
    ),
    ChatMessage(
        role="user",
        content="Tell me a one liner joke about AI.",
    ),
    ChatMessage(
        role="assistant",
        content="Why did the AI go to therapy? Because it had too many unresolved issues!",
    ),
    ChatMessage(
        role="user",
        content="What is the payment status of my transaction T1001?",
    ),
    ChatMessage(
        role="assistant",
        content="""
{
    "functions": [{
        "name": "retrieve_payment_status",
        "parameters": {
            "transaction_id": "T1001"
        }
    }]
}
""",
    ),
    ChatMessage(
        role="user",
        content="#QUERY:\nTell me 3 fun ideas about universe?",
        # content="#QUERY:\nWhat is the current status of my transaction T1002?",
    ),
]


from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1/",
    # required but ignored
    api_key="ollama",
)

# query = "#QUERY:\nTell me 2 fun facts about Jupiter."
query = "#QUERY:\nGive me a summary about my transaction T1005?"

prompts = [
    {
        "name": "payment_transaction",
        "description": "Prompt to answer queries specifically related to payments and transactions.",
    },
    {
        "name": "generic_ai",
        "description": "If the above prompts does not match any criteria. Use this generic prompt to answer queries about anything and everything.",
    },
]

prompts_dict = {
    "payment_transaction": messages[0].content,
    "generic_ai": "You are a helpful assistant.",
}

orig_prompts = [
    {
        "role": "system",
        "content": f"""
You are a prompt identifier who can identify a suitable prompt based on the user's query.
You respond only in JSON.

# JSON SCHEMA OF PROMPTS:

{json.dumps(prompts)}

# YOU MUST FOLLOW THESE INSTRUCTIONS CAREFULLY
<instructions>
- Identify, a prompt which would be suitable to answer the user's query.
- Once you identify the prompt, you must respond in the JSON format matching the following schema:
{{
    "prompt": {{
        "name": "<name of the selected prompt>"
    }}
}}
- Do not provide any additional notes or explanations.
</instructions>
""",
    },
    {
        "role": "user",
        "content": "#QUERY:\nWho are you?",
        # "content": "#QUERY:\nWhat is the current status of my transaction T1002?",
    },
    {
        "role": "assistant",
        "content": """
{
    "prompt": {
        "name": "generic_ai"
    }
}
""",
    },
    {
        "role": "user",
        "content": "#QUERY:\nTell me about Aliens?",
    },
    {
        "role": "assistant",
        "content": """
{
    "prompt": {
        "name": "generic_ai"
    }
}
""",
    },
    {
        "role": "user",
        "content": "#QUERY:\nWhat is the current status of my transaction T1002?",
    },
    {
        "role": "assistant",
        "content": """
{
    "prompt": {
        "name": "payment_transaction"
    }
}
""",
    },
    {
        "role": "user",
        "content": query,
    },
]

response = client.chat.completions.create(
    messages=orig_prompts,
    model="mistral:latest",
    temperature=0,
    response_format={"type": "json_object"},
)

print("selected prompt is: ")
print(response.choices[0].message.content)
prompt_key = json.loads(response.choices[0].message.content)["prompt"]["name"]
prompt_content = prompts_dict.get(prompt_key)

pp = [
    {"role": "system", "content": prompt_content},
    {"role": "user", "content": orig_prompts[-1]["content"]},
]

print("prompting again...")

response = client.chat.completions.create(
    messages=pp,
    model="mistral:latest",
    temperature=0,
    response_format={"type": "json_object"},
)

print("Raw data: " + response.choices[0].message.content)
print("Raw data Completed")

if prompt_key == "payment_transaction":
    func_data = json.loads(response.choices[0].message.content)

    for fn in func_data["functions"]:
        f_name = fn["name"]
        f_args = fn["parameters"]
        print("f_name: ", f_name, "\nf_args: ", f_args)
        print(names_to_functions[f_name](**f_args))

# from mistralai.client import MistralClient
#
# client = MistralClient(api_key="not-needed", endpoint="http://localhost:11434")
# model = "mistral:latest"
#
# response = client.chat(model=model, messages=messages, temperature=0.2)
# print("Raw data: " + response.choices[0].message.content)
# print("Raw data Completed")
# func_data = json.loads(response.choices[0].message.content)
#
# for fn in func_data["functions"]:
#     f_name = fn["name"]
#     f_args = fn["parameters"]
#     print("f_name: ", f_name, "\nf_args: ", f_args)
#     print(names_to_functions[f_name](**f_args))
