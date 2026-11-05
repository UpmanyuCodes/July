"""July in the terminal. Run:  python july.py"""
from july_core import JulyAgent, print_status

print_status()
agent = JulyAgent()

while True:
    user_text = input("\nYou: ")
    if user_text.strip().lower() == "quit":
        break
    print("July:", agent.chat(user_text))