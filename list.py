import os, requests
from dotenv import load_dotenv

load_dotenv()
h = {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"}

u = requests.get("https://api.github.com/user", headers=h)
print("Token valid:", u.status_code)

r = requests.get("https://api.github.com/user/repos?per_page=100&affiliation=owner", headers=h)
print("Repos status:", r.status_code)
if r.status_code == 200:
    for x in r.json():
        print(x["full_name"], "| private" if x["private"] else "| public")