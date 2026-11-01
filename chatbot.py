import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.environ["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

MODEL = "gemini-3.1-flash-lite"

messages = [
    {"role": "system", "content": "You are July, a friendly AI agent. Keep answers short."}
]

print("July is ready. Type 'quit' to stop.")

while True:
    user_text = input("\nYou: ")
    if user_text.lower() == "quit":
        break

    messages.append({"role": "user", "content": user_text})

    try:
        response = client.chat.completions.create(model=MODEL, messages=messages)
    except Exception as e:
        print("July: Sorry, something went wrong:", e)
        messages.pop()
        continue

    reply = response.choices[0].message.content

    messages.append({"role": "assistant", "content": reply})
    print("July:", reply)


