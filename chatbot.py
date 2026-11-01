import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.environ["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
MODEL = "gemini-3.1-flash-lite"
MAX_STEPS = 6  # safety: July can't loop forever


# ---------- TOOL ----------
def github_user_repos(username):
    url = f"https://api.github.com/users/{username}/repos?sort=pushed&per_page=10"
    r = requests.get(url, timeout=15)
    if r.status_code != 200:
        return f"Error {r.status_code}"
    return "\n".join(
        f"{x['name']} | {x['language']} | {x['description']}" for x in r.json()
    )


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "github_user_repos",
            "description": "List the recent public repos of a GitHub user",
            "parameters": {
                "type": "object",
                "properties": {"username": {"type": "string"}},
                "required": ["username"],
            },
        },
    }
]

FUNCTIONS = {"github_user_repos": github_user_repos}


# ---------- MEMORY ----------
messages = [
    {"role": "system", "content": "You are July, a friendly AI agent. Keep answers short. Use tools when needed."}
]


# ---------- THE AGENT LOOP ----------
def ask_july(user_text):
    start = len(messages)
    messages.append({"role": "user", "content": user_text})

    for _ in range(MAX_STEPS):
        try:
            response = client.chat.completions.create(
                model=MODEL, messages=messages, tools=TOOLS
            )
        except Exception as e:
            del messages[start:]  # remove this failed turn from memory
            return f"Sorry, something went wrong: {e}"

        msg = response.choices[0].message
        messages.append(msg)

        # No tool needed: this is the final answer
        if not msg.tool_calls:
            return msg.content

        # Tool needed: run it, send the result back, loop again
        for call in msg.tool_calls:
            name = call.function.name
            try:
                args = json.loads(call.function.arguments)
                print(f"  [July uses tool: {name} {args}]")
                result = FUNCTIONS[name](**args)
            except Exception as e:
                result = f"Error: {e}"
            messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": str(result)}
            )

    return "I took too many steps and stopped."


# ---------- CHAT ----------
print("July is ready. Type 'quit' to stop.")
while True:
    user_text = input("\nYou: ")
    if user_text.lower() == "quit":
        break
    print("July:", ask_july(user_text))