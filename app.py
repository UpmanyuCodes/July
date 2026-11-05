"""July in your browser. Run:  python -m streamlit run app.py"""
import ast
import html
import importlib.util
import os
from datetime import datetime

import streamlit as st

import july_core as core

core.APPROVAL_MODE = "ui"  # approvals become buttons instead of input()

st.set_page_config(
    page_title="July",
    page_icon="☀️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---------- LOOK ----------
# Palette: paper #F3F5F8, ink #16202E, cobalt #2B3FD6 (actions), amber (approvals only)
# Type: Bricolage Grotesque (headings), Instrument Sans (text), JetBrains Mono (code)
STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700&family=Instrument+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --paper: #F3F5F8;
  --surface: #FFFFFF;
  --ink: #16202E;
  --muted: #5B6778;
  --line: #D8DEE8;
  --accent: #2B3FD6;
  --accent-dark: #1F2FA8;
  --amber-soft: #FFF4D9;
  --amber-line: #E7C77A;
  --ok: #1E9E6A;
}

html, body, .stApp { background: var(--paper); color: var(--ink); }
.stApp, p, li, label, textarea, input, button, [data-testid="stMarkdownContainer"] {
  font-family: 'Instrument Sans', system-ui, -apple-system, 'Segoe UI', sans-serif;
}
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li { color: var(--ink); line-height: 1.65; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stAppDeployButton"], #MainMenu, footer { display: none; }
.block-container, [data-testid="stMainBlockContainer"] { max-width: 800px; padding-top: 2.2rem; padding-bottom: 6rem; }

/* ----- sidebar ----- */
[data-testid="stSidebar"] { background: #E9EDF3; border-right: 1px solid var(--line); }
.brand {
  font-family: 'Bricolage Grotesque', system-ui, sans-serif; font-weight: 700;
  font-size: 1.8rem; letter-spacing: -.035em; color: var(--ink);
  display: flex; align-items: flex-start; gap: .3rem; margin: .3rem 0 1.1rem;
}
.sun { width: .55rem; height: .55rem; border-radius: 50%; background: #F2A900; margin-top: .55rem; }
.side-label { font-size: .84rem; font-weight: 600; color: var(--muted); margin: 1.5rem 0 .5rem; }
.conn { display: flex; gap: .6rem; align-items: flex-start; padding: .5rem 0; border-bottom: 1px solid var(--line); }
.conn:last-child { border-bottom: 0; }
.dot { width: .5rem; height: .5rem; border-radius: 50%; background: #A3ADBB; margin-top: .42rem; flex: none; }
.dot.on { background: var(--ok); }
.conn-name { font-weight: 600; font-size: .9rem; color: var(--ink); }
.conn-note { color: var(--muted); font-size: .78rem; line-height: 1.4; }
.facts { max-height: 34vh; overflow-y: auto; }
.fact { font-size: .85rem; line-height: 1.4; padding: .35rem 0 .35rem .7rem; border-left: 2px solid var(--line); margin-bottom: .4rem; color: #2A3547; }
.side-foot { color: var(--muted); font-size: .77rem; line-height: 1.5; margin-top: 1.6rem; }

/* ----- start screen ----- */
.stApp .hero { padding: 2.4rem 0 1.6rem; }
.stApp .hero h1 {
  font-family: 'Bricolage Grotesque', system-ui, sans-serif; font-weight: 700;
  font-size: clamp(2rem, 5.2vw, 3.2rem) !important; letter-spacing: -.035em;
  line-height: 1.04; margin: 0 0 .9rem !important; padding: 0 !important; color: var(--ink);
}
.stApp .hero p { color: var(--muted); font-size: 1.03rem; line-height: 1.55; max-width: 48ch; margin: 0; }
[class*="st-key-prompt_"] button {
  justify-content: flex-start; text-align: left; background: var(--surface);
  border: 1px solid var(--line); border-radius: 12px; padding: .9rem 1rem;
  min-height: 3.4rem; font-weight: 500;
}
[class*="st-key-prompt_"] button p { text-align: left; }

/* ----- buttons ----- */
.stButton > button { width: 100%; border-radius: 10px; font-weight: 600; border: 1px solid var(--line); background: var(--surface); color: var(--ink); transition: border-color .15s, background .15s, color .15s; }
.stButton > button:hover { border-color: var(--accent); color: var(--accent); }
.stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"] { background: var(--accent); border-color: var(--accent); color: #fff; }
.stButton > button[kind="primary"]:hover, .stButton > button[data-testid="stBaseButton-primary"]:hover { background: var(--accent-dark); border-color: var(--accent-dark); color: #fff; }
button:focus-visible, summary:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

/* ----- messages ----- */
[data-testid="stChatMessage"] { background: transparent; padding: .4rem 0; }
[data-testid^="stChatMessageAvatar"] { display: none; }
.user-wrap { display: flex; justify-content: flex-end; }
.user-msg {
  background: var(--surface); border: 1px solid var(--line); border-radius: 14px 14px 4px 14px;
  padding: .65rem .95rem; max-width: 85%; white-space: pre-wrap; line-height: 1.55; color: var(--ink);
}

/* ----- the trail: the steps July took ----- */
details.trail { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: .15rem .95rem; margin: 0 0 .9rem; }
details.trail summary { cursor: pointer; font-weight: 600; font-size: .88rem; color: var(--ink); padding: .5rem 0; list-style: none; }
details.trail summary::-webkit-details-marker { display: none; }
details.trail summary::before { content: "+"; display: inline-block; width: 1.1rem; color: var(--accent); font-weight: 700; }
details.trail[open] summary::before { content: "\\2212"; }
details.trail ol { list-style: none; counter-reset: step; margin: .1rem 0 .6rem; padding: 0; position: relative; }
details.trail ol::before { content: ""; position: absolute; left: .8rem; top: .9rem; bottom: .9rem; width: 1px; background: var(--line); }
details.trail li { counter-increment: step; position: relative; display: grid; grid-template-columns: 1.7rem 1fr; column-gap: .55rem; padding: .35rem 0; }
details.trail li::before {
  content: counter(step); grid-row: 1 / span 2; width: 1.6rem; height: 1.6rem; border-radius: 50%;
  background: var(--surface); border: 1px solid var(--accent); color: var(--accent);
  font-size: .76rem; font-weight: 600; display: grid; place-items: center; position: relative; z-index: 1;
}
.t-main { font-size: .9rem; font-weight: 500; line-height: 1.6rem; color: var(--ink); }
.t-code, .t-detail { font-family: 'JetBrains Mono', ui-monospace, Consolas, monospace; font-size: .75rem; color: var(--muted); }
.t-code { margin-left: .5rem; background: #EEF1F6; border-radius: 6px; padding: .05rem .35rem; }
.t-detail { grid-column: 2; line-height: 1.4; word-break: break-word; }

/* ----- approval card ----- */
.st-key-approval { background: var(--amber-soft); border: 1px solid var(--amber-line); border-radius: 14px; padding: 1rem 1.1rem 1.1rem; margin: .6rem 0 1rem; }
.ap-title { font-family: 'Bricolage Grotesque', system-ui, sans-serif; font-weight: 700; font-size: 1.2rem; color: #5E3F08; }
.ap-copy { color: #6B5520; font-size: .9rem; margin: .2rem 0 .3rem; }
.st-key-approval pre { white-space: pre-wrap !important; word-break: break-word; background: var(--surface) !important; border: 1px solid var(--amber-line); border-radius: 10px; }
code, pre { font-family: 'JetBrains Mono', ui-monospace, Consolas, monospace !important; }

/* ----- input ----- */
[data-testid="stBottom"] > div { background: var(--paper); }
[data-testid="stChatInput"] { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; }
[data-testid="stChatInput"]:focus-within { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(43, 63, 214, .14); }
[data-testid="stChatInput"] textarea { color: var(--ink); }

@media (max-width: 640px) { .user-msg { max-width: 95%; } }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>
"""
st.markdown(STYLE, unsafe_allow_html=True)


# ---------- WORDS ----------
TOOL_LABELS = {
    "list_repos": "List GitHub repositories",
    "repo_details": "Open a repository",
    "list_files": "Browse repository files",
    "read_file": "Read a repository file",
    "recent_commits": "Check recent commits",
    "list_issues": "Check issues and pull requests",
    "search_code": "Search code on GitHub",
    "write_file": "Edit a GitHub file",
    "list_data_files": "Look in the data folder",
    "csv_summary": "Summarize a CSV file",
    "group_stats": "Group CSV data",
    "plot_chart": "Draw a chart",
    "update_csv_cell": "Edit a CSV value",
    "send_email": "Send an email",
    "read_emails": "Read the inbox",
    "read_email_body": "Open an email",
    "notice_radar": "Scan for notices",
    "web_search": "Search the web",
    "save_memory": "Save to memory",
    "list_memory": "Read memory",
    "forget_memory": "Forget a fact",
}

# title from july_core -> (heading, what happens, approve button)
APPROVALS = {
    "JULY WANTS TO CHANGE A FILE": (
        "Change a file on GitHub?",
        "The change goes to a new branch with a pull request. Nothing on main changes until you merge it.",
        "Apply change",
    ),
    "JULY WANTS TO CHANGE A CSV CELL": (
        "Change a value in a CSV file?",
        "A backup of the file is saved first.",
        "Apply change",
    ),
    "JULY WANTS TO SEND AN EMAIL": (
        "Send this email?",
        "It is sent from your Gmail account.",
        "Send email",
    ),
    "JULY WANTS TO FORGET A FACT": (
        "Forget this fact?",
        "It is removed from your saved memory.",
        "Forget fact",
    ),
}

PROMPTS = [
    "List my GitHub repositories",
    "Summarize samples.csv",
    "Check my notices from the last 7 days",
    "Show my last 5 emails",
    "Search the web for robotics news",
    "What do you remember about me?",
]


# ---------- HELPERS ----------
def esc(text):
    return html.escape(str(text), quote=True)


def greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    if hour < 18:
        return "Good afternoon"
    return "Good evening"


def parse_step(line):
    """'read_file {'repo': 'a/b'}'  ->  ('read_file', 'repo=a/b')"""
    name, _, rest = line.partition(" ")
    detail = rest
    try:
        data = ast.literal_eval(rest)
        if isinstance(data, dict):
            detail = ", ".join(f"{k}={v}" for k, v in data.items() if v not in ("", None))
    except Exception:
        pass
    return name, detail[:110]


def trail_html(tools):
    items = ""
    for line in tools:
        name, detail = parse_step(line)
        items += (
            f'<li><span class="t-main">{esc(TOOL_LABELS.get(name, name))}'
            f'<code class="t-code">{esc(name)}</code></span>'
            + (f'<span class="t-detail">{esc(detail)}</span>' if detail else "")
            + "</li>"
        )
    count = len(tools)
    word = "step" if count == 1 else "steps"
    return (
        f'<details class="trail"><summary>July took {count} {word}</summary>'
        f"<ol>{items}</ol></details>"
    )


def render_message(item):
    with st.chat_message(item["role"]):
        if item["role"] == "user":
            st.markdown(
                f'<div class="user-wrap"><div class="user-msg">{esc(item["content"])}</div></div>',
                unsafe_allow_html=True,
            )
            return
        if item.get("tools"):
            st.markdown(trail_html(item["tools"]), unsafe_allow_html=True)
        for path in item.get("images", []):
            if os.path.exists(path):
                st.image(path)
        st.markdown(item["content"])


# ---------- STATE (kept while the browser tab is open) ----------
def new_chat():
    st.session_state.agent = core.JulyAgent()
    st.session_state.chat = []  # each item: role, content, tools, images


if "agent" not in st.session_state:
    new_chat()

agent = st.session_state.agent


def finish_turn(result):
    """If July finished answering, save the answer in the chat history."""
    if result["status"] == "done":
        tools, images = agent.take_log()
        st.session_state.chat.append(
            {"role": "assistant", "content": result["text"], "tools": tools, "images": images}
        )


def safe_ask(text):
    try:
        return agent.ask(text)
    except Exception as e:  # keep the page alive, and say what happened
        return {"status": "done", "text": f"July could not finish that request. Details: {e}"}


# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown('<div class="brand">July<span class="sun"></span></div>', unsafe_allow_html=True)

    if st.button("New conversation", key="new_chat"):
        new_chat()
        st.rerun()

    github_on = bool(core.GITHUB_TOKEN)
    if core.WRITE_REPOS:
        write_note = "Can edit: " + ", ".join(sorted(core.WRITE_REPOS))
    else:
        write_note = "Read-only."
    email_on = bool(core.EMAIL_ADDRESS and core.EMAIL_APP_PASSWORD)
    search_on = importlib.util.find_spec("ddgs") is not None

    rows = [
        (
            "GitHub",
            github_on,
            ("Connected. " if github_on else "Public repositories only. ") + write_note,
        ),
        (
            "Email",
            email_on,
            "Send and read through Gmail."
            if email_on
            else "Not set up. Add EMAIL_ADDRESS and EMAIL_APP_PASSWORD to .env.",
        ),
        (
            "Web search",
            search_on,
            "Ready." if search_on else "Run: python -m pip install ddgs",
        ),
    ]
    st.markdown('<div class="side-label">Connections</div>', unsafe_allow_html=True)
    st.markdown(
        "".join(
            f'<div class="conn"><span class="dot{" on" if on else ""}"></span>'
            f'<div><div class="conn-name">{esc(name)}</div>'
            f'<div class="conn-note">{esc(note)}</div></div></div>'
            for name, on, note in rows
        ),
        unsafe_allow_html=True,
    )

    facts = core.load_memory()
    st.markdown(f'<div class="side-label">Memory ({len(facts)})</div>', unsafe_allow_html=True)
    if facts:
        st.markdown(
            '<div class="facts">'
            + "".join(f'<div class="fact">{esc(f)}</div>' for f in facts)
            + "</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="conn-note">Nothing saved yet. Ask July to remember something.</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="side-foot">July asks before it sends email, edits files or data, '
        "or forgets a fact. Run this app only on your own computer.</div>",
        unsafe_allow_html=True,
    )


# ---------- MAIN ----------
queued = st.session_state.pop("queued", None)  # a starter prompt that was clicked

if not st.session_state.chat and not agent.pending and not queued:
    st.markdown(
        f'<div class="hero"><h1>{greeting()}.<br>What should July do?</h1>'
        "<p>July can read your GitHub and inbox, analyze CSV files, search the web "
        "and remember things. It asks before it changes anything.</p></div>",
        unsafe_allow_html=True,
    )
    columns = st.columns(2)
    for i, text in enumerate(PROMPTS):
        if columns[i % 2].button(text, key=f"prompt_{i}"):
            st.session_state.queued = text
            st.rerun()

for item in st.session_state.chat:
    render_message(item)

# ----- approval card (shown when July wants to change something) -----
if agent.pending:
    p = agent.pending
    heading, copy, go_label = APPROVALS.get(
        p["title"], (p["title"].capitalize(), "Review the details, then choose.", "Approve")
    )
    with st.container(key="approval"):
        st.markdown(
            f'<div class="ap-title">{esc(heading)}</div><div class="ap-copy">{esc(copy)}</div>',
            unsafe_allow_html=True,
        )
        st.code("\n".join(p["lines"]), language=None)
        left, right, _ = st.columns([1.3, 1, 2])
        if left.button(go_label, key="approve_btn", type="primary"):
            with st.spinner("July is working..."):
                finish_turn(agent.decide(True))
            st.rerun()
        if right.button("Cancel", key="reject_btn"):
            with st.spinner("July is working..."):
                finish_turn(agent.decide(False))
            st.rerun()

# ----- input -----
typed = st.chat_input(
    "Choose an option above to continue." if agent.pending else "Message July",
    disabled=bool(agent.pending),
)
text = queued or typed
if text and not agent.pending:
    user_item = {"role": "user", "content": text}
    st.session_state.chat.append(user_item)
    render_message(user_item)
    with st.spinner("July is working..."):
        finish_turn(safe_ask(text))
    st.rerun()

