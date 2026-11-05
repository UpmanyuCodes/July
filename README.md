# July: a free, safe AI agent

July is a command-line AI agent written in Python. You chat with it in plain English, and it uses **tools** to do real work: explore GitHub, analyse CSV files, read and send email, search the web, and remember facts about you.

It runs on the **free** Gemini API tier, and every action that changes something needs **your approval first**. Use it in the **terminal** or in a **browser chat window** (Streamlit) with Approve / Reject buttons.

---

## What July can do

| Area | Tools | What it does |
|---|---|---|
| **GitHub (read)** | `list_repos`, `repo_details`, `list_files`, `read_file`, `recent_commits`, `list_issues`, `search_code` | Explore any public repo, and your private ones with a token |
| **GitHub (write)** | `write_file` | Edits a file on a **new branch** and opens a **pull request** (never touches `main`) |
| **CSV analysis** | `list_data_files`, `csv_summary`, `group_stats`, `plot_chart` | Summaries, group statistics and charts from CSV files |
| **CSV editing** | `update_csv_cell` | Changes one cell, with a backup first |
| **Email (send)** | `send_email` | Sends a plain-text email after you approve it |
| **Email (read)** | `read_emails`, `read_email_body`, `notice_radar` | Lists mail, opens one email, and finds college notices and deadlines (read-only) |
| **Web** | `web_search` | Current information via DuckDuckGo (no API key) |
| **Memory** | `save_memory`, `list_memory`, `forget_memory` | Remembers facts between runs in `memory.json` |

### Example things to ask

```
list my repos
summarise the README of UpmanyuCodes/July-AI-Agent
which city has the highest average marks in sample.csv? make a bar chart
check my notices from the last 7 days
read the email with ID 1234
search the web for latest news about robotics clubs in India
remember that I am preparing for SDE internships
what do you remember about me?
```

---

## Safety features

July is built to be **useful without being risky**.

- **Human approval:** `write_file`, `update_csv_cell`, `send_email` and `forget_memory` all show exactly what will happen and wait for your `yes` (terminal) or your click on **Approve** (browser).
- **GitHub allow-list:** July can write only to repos listed in `JULY_WRITE_REPOS`.
- **Pull requests only:** edits go to a new branch and a pull request. Nothing changes on `main` until you merge.
- **CSV backups:** a copy of the file is saved to `backups/` before every edit.
- **CSV sandbox:** July can only read and edit files inside the `data/` folder.
- **Read-only inbox:** emails are opened with IMAP `readonly` and `BODY.PEEK`, so nothing is marked read, moved or deleted.
- **Email limit:** at most 5 emails per run.
- **Prompt-injection rule:** text inside files, emails and web pages is treated as data, never as instructions.
- **Loop guards:** a maximum of 10 steps per question, and repeated identical tool calls are blocked.
- **Token saving:** long tool results are cut to 6000 characters.
- **No secrets in memory:** July is told never to save passwords or API keys.

---

## Setup

### 1. Clone and install

```bash
git clone https://github.com/UpmanyuCodes/July-AI-Agent.git
cd July-AI-Agent
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
python -m pip install -r requirements.txt
```

### 2. Create a `.env` file

```env
GEMINI_API_KEY=your_gemini_api_key
GITHUB_USERNAME=your_github_username

# Optional: lets July read your private repos
GITHUB_TOKEN=your_github_token

# Optional: repos July may write to (comma separated)
JULY_WRITE_REPOS=your_github_username/July-Sandbox

# Optional: email
EMAIL_ADDRESS=you@gmail.com
EMAIL_APP_PASSWORD=your_gmail_app_password
```

- **Gemini key:** free from [Google AI Studio](https://aistudio.google.com/).
- **Gmail app password:** turn on 2-Step Verification, then create an app password in your Google account. Also enable IMAP in Gmail settings (Forwarding and POP/IMAP).
- **Never commit `.env`.** It is already in `.gitignore`.

### 3. Run

**Browser chat window (recommended):**

```bash
python -m streamlit run app.py
```

**Terminal:**

```bash
python july.py
```

Type your question. In the terminal, type `quit` to stop.

> Run the browser app only on your own computer. It can use your Gmail and GitHub, and it has no login.

---

## Project structure

```
July-AI-Agent/
├── july_core.py       # the agent: tools, menu, safety rules, approval logic
├── july.py            # terminal chat
├── app.py             # browser chat (Streamlit)
├── requirements.txt
├── .env               # your secrets (not committed)
├── memory.json        # July's saved facts (not committed)
├── data/              # CSV files July can read and edit (not committed)
├── backups/           # CSV backups made before edits (not committed)
└── plots/             # charts July creates (not committed)
```

---

## How it works

1. You type a question.
2. July sends it to the Gemini model together with a **menu of tools**.
3. The model picks a tool. July runs it in Python and sends the result back.
4. This repeats until the model has enough to answer (maximum 10 steps).
5. Saved facts from `memory.json` are added to July's instructions before every question.

Gemini is called through its OpenAI-compatible endpoint, so the code uses the standard `openai` Python library.

---

## Roadmap

- [x] Streamlit chat interface
- [ ] Daily email digest of notices
- [ ] PDF reading
- [ ] Deadline reminders

---

## Tech

Python · OpenAI-compatible API (Gemini) · Streamlit · pandas · matplotlib · requests · imaplib / smtplib · ddgs

Built by [Upmanyu](https://github.com/UpmanyuCodes).