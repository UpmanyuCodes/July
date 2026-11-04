# July AI Agent

July is a terminal-based AI assistant that can work with GitHub repositories, analyze local CSV files, create charts, update CSV values, and send emails with human approval.

July uses the OpenAI-compatible Gemini API through the `openai` Python package.

## Features

- List GitHub repositories and inspect repository details.
- Browse repository files, read files, view recent commits, and list issues.
- Search GitHub code.
- Create or replace a file in an allowed repository through a new branch and pull request.
- List and summarize local CSV files.
- Calculate grouped CSV statistics.
- Create histogram, bar, line, and scatter charts.
- Update exactly one CSV cell after confirmation.
- Create a backup before each approved CSV edit.
- Send plain-text email through Gmail after confirmation.

## Requirements

- Windows
- Python 3.10 or newer
- A Gemini API key
- A GitHub token for GitHub access
- A Gmail app password if email sending is needed

## Setup

1. Create and activate a virtual environment:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. Install the dependencies:

   ```powershell
   pip install openai python-dotenv requests pandas matplotlib
   ```

3. Create a `.env` file in the project root:

   ```env
   GEMINI_API_KEY=your_gemini_api_key
   GITHUB_TOKEN=your_github_token
   GITHUB_USERNAME=your_github_username
   JULY_WRITE_REPOS=owner/allowed-repository
   EMAIL_ADDRESS=your_gmail_address
   EMAIL_APP_PASSWORD=your_gmail_app_password
   ```

   Keep `.env` private. Never commit API keys, tokens, or app passwords.

4. Start July:

   ```powershell
   python july.py
   ```

   On this Windows setup, `july.bat` can also be used to start the application.

## Configuration and safety

- Without `JULY_WRITE_REPOS`, GitHub access is read-only.
- GitHub writes are limited to repositories listed in `JULY_WRITE_REPOS`.
- July asks for approval before changing a CSV cell.
- A CSV is copied to `backups\` before an approved edit.
- July asks for approval before sending email.
- A maximum of five emails can be sent in one run.
- Local CSV files are read only from the `data\` folder.
- Charts are saved in the `plots\` folder.
- If `data\` is empty, July creates `data\sample.csv` for practice.

## Example requests

After starting July, try:

```text
List my GitHub repositories.
Show the details of UpmanyuCodes/July.
Summarize sample.csv.
What is the average marks by city in sample.csv?
Create a bar chart of marks by city in sample.csv.
Change Meera's marks to 95 in sample.csv.
```

Type `quit` to exit.

## Project folders

```text
data\       Local CSV files
plots\      Generated chart images
backups\    Backups made before CSV edits
venv\       Local Python virtual environment
july.py     July application
july.bat    Windows launcher
.env        Local configuration and secrets
```

## Important notes

GitHub file changes are made through a new branch and pull request. Review and merge the pull request on GitHub before treating a change as final.

July can only perform actions exposed through its tool list. It does not automatically execute arbitrary commands or modify files outside its configured operations.
