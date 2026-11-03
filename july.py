import os
import json
import time
import base64
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ---------- SETTINGS ----------
client = OpenAI(
    api_key=os.environ["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
MODEL = "gemini-3.1-flash-lite"
MAX_STEPS = 10      # safety: July can't loop forever
MAX_CHARS = 6000    # cut long tool results to save free tokens

GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME", "UpmanyuCodes")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")  # connects July to YOUR account

# Safety list: July may write ONLY to these repos (comma separated in .env)
# Example in .env:  JULY_WRITE_REPOS=UpmanyuCodes/july-sandbox
WRITE_REPOS = {
    r.strip().lower()
    for r in os.environ.get("JULY_WRITE_REPOS", "").split(",")
    if r.strip()
}


# ---------- HELPERS ----------
def gh(path, params=None, raw=False):
    """Read from the GitHub API."""
    accept = "application/vnd.github.raw+json" if raw else "application/vnd.github+json"
    headers = {"Accept": accept}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return requests.get(
        f"https://api.github.com{path}", headers=headers, params=params, timeout=20
    )


def gh_send(method, path, body):
    """Write to the GitHub API (POST / PUT)."""
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
    }
    return requests.request(
        method, f"https://api.github.com{path}", headers=headers, json=body, timeout=20
    )


def short(text):
    if len(text) <= MAX_CHARS:
        return text
    return text[:MAX_CHARS] + "\n...[cut: too long]"


# ---------- READ TOOLS ----------
def list_repos(username=None):
    mine = (username is None) or (username.lower() == GITHUB_USERNAME.lower())
    if GITHUB_TOKEN and mine:
        r = gh("/user/repos", {"sort": "pushed", "per_page": 50, "affiliation": "owner"})
    else:
        r = gh(f"/users/{username or GITHUB_USERNAME}/repos", {"sort": "pushed", "per_page": 50})
    if r.status_code != 200:
        return f"Error {r.status_code}"
    lines = []
    for x in r.json():
        kind = "private" if x["private"] else "public"
        lines.append(
            f"{x['full_name']} | {kind} | {x['language']} | "
            f"pushed {x['pushed_at'][:10]} | {x['description']}"
        )
    return short("\n".join(lines))


def repo_details(repo):
    r = gh(f"/repos/{repo}")
    if r.status_code != 200:
        return f"Error {r.status_code}: repo not found or private"
    d = r.json()
    langs = list(gh(f"/repos/{repo}/languages").json().keys())
    rd = gh(f"/repos/{repo}/readme", raw=True)
    readme = rd.text if rd.status_code == 200 else "No README found."
    return short(
        f"Name: {d['full_name']}\nDescription: {d['description']}\n"
        f"Stars: {d['stargazers_count']} | Forks: {d['forks_count']} | "
        f"Open issues: {d['open_issues_count']}\n"
        f"Created: {d['created_at']} | Last push: {d['pushed_at']}\n"
        f"Languages: {langs}\n\nREADME:\n{readme}"
    )


def list_files(repo, path=""):
    r = gh(f"/repos/{repo}/contents/{path}")
    if r.status_code != 200:
        return f"Error {r.status_code}: path not found"
    data = r.json()
    if isinstance(data, dict):
        return "That path is a file. Use read_file instead."
    lines = [
        f"{'[folder]' if x['type'] == 'dir' else '[file]'} {x['path']} ({x['size']} bytes)"
        for x in data
    ]
    return short("\n".join(lines))


def read_file(repo, path):
    r = gh(f"/repos/{repo}/contents/{path}", raw=True)
    if r.status_code != 200:
        return f"Error {r.status_code}: file not found"
    if "\x00" in r.text[:2000]:
        return "This is a binary file (image, zip, etc.). Cannot read it as text."
    return short(r.text)


def recent_commits(repo, count=10):
    r = gh(f"/repos/{repo}/commits", {"per_page": min(int(count), 30)})
    if r.status_code != 200:
        return f"Error {r.status_code}"
    lines = []
    for c in r.json():
        info = c["commit"]
        lines.append(
            f"{info['author']['date'][:10]} | {info['author']['name']} | "
            f"{info['message'].splitlines()[0]}"
        )
    return short("\n".join(lines))


def list_issues(repo, state="open"):
    r = gh(f"/repos/{repo}/issues", {"state": state, "per_page": 20})
    if r.status_code != 200:
        return f"Error {r.status_code}"
    lines = [
        f"#{i['number']} [{'PR' if 'pull_request' in i else 'issue'}] {i['title']} ({i['state']})"
        for i in r.json()
    ]
    return short("\n".join(lines)) or "No issues found."


def search_code(query, repo=None):
    if not GITHUB_TOKEN:
        return "Code search needs a GITHUB_TOKEN in .env. Use list_files and read_file instead."
    q = f"{query} repo:{repo}" if repo else f"{query} user:{GITHUB_USERNAME}"
    r = gh("/search/code", {"q": q, "per_page": 10})
    if r.status_code != 200:
        return f"Error {r.status_code}"
    items = r.json().get("items", [])
    if not items:
        return "No matches."
    return short("\n".join(f"{i['repository']['full_name']}: {i['path']}" for i in items))


# ---------- WRITE TOOL (safe: allow-list + approval + new branch + pull request) ----------
session_branches = {}  # one branch per repo per run, so many edits go in one pull request


def write_file(repo, path, content, commit_message):
    # Safety 1: token and allow-list
    if not GITHUB_TOKEN:
        return "No GITHUB_TOKEN set in .env. Cannot write."
    if repo.lower() not in WRITE_REPOS:
        return (
            f"Writing to {repo} is NOT allowed. "
            f"Allowed repos: {sorted(WRITE_REPOS) or 'none (set JULY_WRITE_REPOS in .env)'}"
        )
    if ".." in path or path.startswith("/"):
        return "Invalid file path."

    # Safety 2: human approval
    print("\n=========== JULY WANTS TO CHANGE A FILE ===========")
    print(f"Repo   : {repo}")
    print(f"File   : {path}")
    print(f"Message: {commit_message}")
    print(f"New content (first 1500 characters):\n{content[:1500]}")
    print("====================================================")
    if input("Apply this change? (yes/no): ").strip().lower() != "yes":
        return "User said no. Nothing was changed."

    # Find the main branch
    info = gh(f"/repos/{repo}")
    if info.status_code != 200:
        return f"Cannot open repo: {info.status_code}. Check token access."
    base = info.json()["default_branch"]

    # Safety 3: work on a NEW branch, never on main
    key = repo.lower()
    first_edit = key not in session_branches
    if first_edit:
        ref = gh(f"/repos/{repo}/git/ref/heads/{base}")
        if ref.status_code != 200:
            return (
                f"Cannot read branch '{base}': {ref.status_code}. "
                "The repo may be empty. Add a README first."
            )
        branch = f"july/{int(time.time())}"
        r = gh_send(
            "POST", f"/repos/{repo}/git/refs",
            {"ref": f"refs/heads/{branch}", "sha": ref.json()["object"]["sha"]},
        )
        if r.status_code != 201:
            return f"Could not create branch: {r.status_code} {r.text[:200]}"
        session_branches[key] = branch
    branch = session_branches[key]

    # If the file already exists, GitHub needs its current id (sha)
    body = {
        "message": commit_message,
        "content": base64.b64encode(content.encode("utf-8")).decode(),
        "branch": branch,
    }
    existing = gh(f"/repos/{repo}/contents/{path}", {"ref": branch})
    if existing.status_code == 200:
        body["sha"] = existing.json()["sha"]

    r = gh_send("PUT", f"/repos/{repo}/contents/{path}", body)
    if r.status_code not in (200, 201):
        return f"Could not write file: {r.status_code} {r.text[:200]}"

    # Open a pull request on the first edit, so you can review it on GitHub
    result = f"File '{path}' saved on branch '{branch}'."
    if first_edit:
        pr = gh_send(
            "POST", f"/repos/{repo}/pulls",
            {
                "title": f"July: {commit_message}",
                "head": branch,
                "base": base,
                "body": "Created by July (AI agent). Please review before merging.",
            },
        )
        if pr.status_code == 201:
            result += f" Pull request: {pr.json()['html_url']}"
        else:
            result += f" (Could not open pull request: {pr.status_code})"
    return result + " Nothing on the main branch has changed. The user must review and merge."


# ---------- THE MENU (what the LLM reads) ----------
def tool(name, description, props, required):
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {"type": "object", "properties": props, "required": required},
        },
    }


S = {"type": "string"}
TOOLS = [
    tool("list_repos",
         "List GitHub repos of a user, newest activity first. Leave username empty for the owner's own repos.",
         {"username": S}, []),
    tool("repo_details",
         "Get description, languages, stars, dates and README of one repo. repo format: owner/name.",
         {"repo": S}, ["repo"]),
    tool("list_files",
         "List files and folders inside a repo folder. Leave path empty for the root folder.",
         {"repo": S, "path": S}, ["repo"]),
    tool("read_file",
         "Read the text content of one file in a repo, for example main.py or src/app.js.",
         {"repo": S, "path": S}, ["repo", "path"]),
    tool("recent_commits",
         "Get the latest commits (date, author, message) of a repo.",
         {"repo": S, "count": {"type": "integer"}}, ["repo"]),
    tool("list_issues",
         "List issues and pull requests of a repo. state: open, closed or all.",
         {"repo": S, "state": S}, ["repo"]),
    tool("search_code",
         "Search for text inside code files. Optional repo in owner/name format.",
         {"query": S, "repo": S}, ["query"]),
    tool("write_file",
         "Create or replace ONE file in an allowed repo, on a new branch with a pull request. "
         "The human approves first. Always give the FULL new content of the file. "
         "To edit an existing file, read it first with read_file, then send the whole updated file.",
         {"repo": S, "path": S, "content": S, "commit_message": S},
         ["repo", "path", "content", "commit_message"]),
]

FUNCTIONS = {
    "list_repos": list_repos,
    "repo_details": repo_details,
    "list_files": list_files,
    "read_file": read_file,
    "recent_commits": recent_commits,
    "list_issues": list_issues,
    "search_code": search_code,
    "write_file": write_file,
}

SYSTEM = f"""You are July, a friendly AI agent that explores and edits GitHub using tools.
The owner's GitHub username is {GITHUB_USERNAME}.
Rules:
- Never guess. Get real data with tools before answering.
- Explore step by step: list repos, then repo details, then list files, then read files.
- Repo names must be in owner/name format, like {GITHUB_USERNAME}/July-AI-Agent.
- Only change files when the user clearly asks for a change.
- Before editing an existing file, read it first. Then send the FULL updated file, without losing old parts.
- After a change, tell the user the branch and the pull request link, and say they must review and merge it.
- If a tool returns an error, tell the user honestly. Never pretend a change worked.
- If you have no tool for something, say so.
- Keep answers short and simple."""

messages = [{"role": "system", "content": SYSTEM}]


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
            del messages[start:]  # remove the failed turn from memory
            return f"Sorry, something went wrong: {e}"

        msg = response.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:  # no tool needed: final answer
            return msg.content

        for call in msg.tool_calls:  # run each requested tool
            name = call.function.name
            try:
                args = json.loads(call.function.arguments)
                shown = {k: (v if k != "content" else "...") for k, v in args.items()}
                print(f"  [July uses tool: {name} {shown}]")
                result = FUNCTIONS[name](**args)
            except Exception as e:
                result = f"Error: {e}"
            messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": str(result)}
            )

    return "I took too many steps and stopped. Try a more specific question."


# ---------- CHAT ----------
print("July is ready. Ask me anything about GitHub. Type 'quit' to stop.")
if WRITE_REPOS:
    print(f"Write access allowed only for: {sorted(WRITE_REPOS)}")
else:
    print("Read-only mode (set JULY_WRITE_REPOS in .env to allow edits).")

while True:
    user_text = input("\nYou: ")
    if user_text.lower() == "quit":
        break
    print("July:", ask_july(user_text))