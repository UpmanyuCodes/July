"""July in your browser. Run:  python -m streamlit run app.py"""
import ast
import html
import os
import shutil
import uuid
from datetime import datetime

import streamlit as st

import july_core as core

core.APPROVAL_MODE = "ui"  # approvals become buttons instead of input()

st.set_page_config(
    page_title="July",
    page_icon="☀️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------- LOOK ----------
# Pale cool paper, ink-navy text, one cobalt-to-violet-to-cyan "light" that July itself glows with.
# Type: Bricolage Grotesque (headings), Instrument Sans (text), JetBrains Mono (code)
STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700&family=Instrument+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --paper: #F4F6FA;
  --surface: #FFFFFF;
  --ink: #131C2B;
  --muted: #5E6A7D;
  --line: #DCE2EC;
  --accent: #2B3FD6;
  --accent-dark: #1F2FA8;
  --violet: #7A5CFF;
  --cyan: #22D3EE;
  --amber-soft: #FFF7E2;
  --amber-line: #EBCB85;
}

/* ----- page: dot grid and a soft aurora behind everything ----- */
html, body { background: var(--paper); }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stHeader"] { background: transparent !important; color: var(--ink); }
body::before {
  content: ""; position: fixed; inset: 0; z-index: -1; pointer-events: none;
  background-image: radial-gradient(rgba(19, 28, 43, .10) 1px, transparent 1px);
  background-size: 24px 24px;
  -webkit-mask-image: radial-gradient(ellipse 75% 60% at 50% 18%, #000 0%, transparent 75%);
  mask-image: radial-gradient(ellipse 75% 60% at 50% 18%, #000 0%, transparent 75%);
}
body::after {
  content: ""; position: fixed; inset: 0; z-index: -1; pointer-events: none;
  background:
    radial-gradient(520px 300px at 50% 6%, rgba(122, 92, 255, .20), transparent 70%),
    radial-gradient(420px 260px at 28% 14%, rgba(34, 211, 238, .16), transparent 70%),
    radial-gradient(420px 260px at 74% 12%, rgba(43, 63, 214, .14), transparent 70%);
}

.stApp, p, li, label, textarea, input, button, [data-testid="stMarkdownContainer"] {
  font-family: 'Instrument Sans', system-ui, -apple-system, 'Segoe UI', sans-serif;
}
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li { color: var(--ink); line-height: 1.65; }
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
[data-testid="stAppDeployButton"], [data-testid="stToolbar"], #MainMenu, footer { display: none !important; }
.block-container, [data-testid="stMainBlockContainer"] { max-width: 760px; padding-top: 1.4rem; padding-bottom: 7rem; }

/* ----- top bar ----- */
.brand {
  font-family: 'Bricolage Grotesque', system-ui, sans-serif; font-weight: 700;
  font-size: 1.45rem; letter-spacing: -.035em; color: var(--ink);
  display: flex; align-items: flex-start; gap: .28rem; padding-top: .25rem;
}
.sun { width: .45rem; height: .45rem; border-radius: 50%; background: #F2A900; margin-top: .42rem; }
.st-key-new_chat .stButton { display: flex; justify-content: flex-end; }
.st-key-new_chat button { width: auto; background: rgba(255, 255, 255, .7); backdrop-filter: blur(6px); }

/* ----- July's orb: the one memorable thing ----- */
.orb { position: relative; width: 108px; height: 108px; margin: 0 auto 1.6rem; border-radius: 50%; animation: breathe 7s ease-in-out infinite; }
.orb i, .mini-orb i { position: absolute; inset: 0; border-radius: 50%; display: block; }
.orb-core {
  background: conic-gradient(from 0deg, #2B3FD6, #7A5CFF, #22D3EE, #7A5CFF, #2B3FD6);
  box-shadow: 0 0 80px rgba(86, 100, 255, .50), 0 0 24px rgba(34, 211, 238, .35);
  filter: blur(1.2px); animation: spin 16s linear infinite;
}
.orb-gloss {
  background:
    radial-gradient(circle at 31% 25%, rgba(255, 255, 255, .95), rgba(255, 255, 255, 0) 42%),
    radial-gradient(circle at 72% 82%, rgba(19, 28, 43, .38), rgba(19, 28, 43, 0) 58%);
}
.orb-ring {
  inset: -10px !important; border: 1px solid rgba(43, 63, 214, .40);
  border-top-color: transparent; border-left-color: transparent; animation: spin 10s linear infinite reverse;
}
.mini-orb { position: relative; display: inline-block; width: 22px; height: 22px; border-radius: 50%; flex: none; }
.mini-orb .orb-core { box-shadow: 0 0 16px rgba(86, 100, 255, .55); filter: none; animation-duration: 3s; }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes breathe { 50% { transform: scale(1.045); } }
@keyframes shimmer { to { background-position: -200% 0; } }

/* ----- start screen ----- */
.stApp .hero { text-align: center; padding: 3.2rem 0 1.4rem; }
.stApp .hero h1 {
  font-family: 'Bricolage Grotesque', system-ui, sans-serif; font-weight: 700;
  font-size: clamp(2.2rem, 6vw, 3.4rem) !important; letter-spacing: -.04em; line-height: 1.05;
  margin: 0 0 .5rem !important; padding: 0 !important; color: var(--ink);
}
.stApp .hero p { color: var(--muted); font-size: 1.15rem; margin: 0; }
.st-key-starters { flex-direction: row !important; flex-wrap: wrap; justify-content: center; gap: .6rem !important; margin-top: 1.2rem; }
.st-key-starters .stElementContainer, .st-key-starters .stButton { width: auto !important; }
.st-key-starters button {
  width: auto; border-radius: 999px; padding: .55rem 1.1rem; min-height: 0; font-weight: 500;
  background: rgba(255, 255, 255, .78); backdrop-filter: blur(6px);
}
.st-key-starters button:hover { transform: translateY(-1px); box-shadow: 0 8px 26px rgba(43, 63, 214, .16); }

/* ----- buttons ----- */
.stButton > button {
  border-radius: 10px; font-weight: 600; border: 1px solid var(--line); background: var(--surface); color: var(--ink);
  transition: border-color .15s, background .15s, color .15s, box-shadow .2s, transform .2s;
}
.stButton > button:hover { border-color: var(--accent); color: var(--accent); }
.stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"] { background: var(--accent); border-color: var(--accent); color: #fff; }
.stButton > button[kind="primary"]:hover, .stButton > button[data-testid="stBaseButton-primary"]:hover { background: var(--accent-dark); border-color: var(--accent-dark); color: #fff; }
.stButton button p { color: inherit !important; }
button:focus-visible, summary:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

/* ----- messages ----- */
[data-testid="stChatMessage"] { background: transparent; padding: .45rem 0; gap: .8rem; }
[data-testid="stChatMessageAvatarUser"] { display: none; }
[data-testid="stChatMessageAvatarAssistant"] {
  width: 26px !important; height: 26px !important; min-width: 26px; border-radius: 50% !important; margin-top: .15rem;
  background: conic-gradient(from 30deg, #2B3FD6, #7A5CFF, #22D3EE, #2B3FD6) !important;
  box-shadow: 0 0 16px rgba(86, 100, 255, .5); color: transparent !important; overflow: hidden;
}
[data-testid="stChatMessageAvatarAssistant"] * { display: none !important; }
.user-wrap { display: flex; justify-content: flex-end; padding: 2px 6px 8px 2px; }
.user-msg {
  background: var(--surface); border: 1px solid var(--line); border-radius: 16px 16px 4px 16px;
  padding: .65rem 1rem; max-width: 85%; white-space: pre-wrap; line-height: 1.55; color: var(--ink);
  box-shadow: 0 4px 18px rgba(19, 28, 43, .05);
}

/* ----- thinking indicator ----- */
.thinking { display: flex; align-items: center; gap: .7rem; padding: .4rem 0 .4rem .1rem; }
.shimmer {
  font-weight: 600; font-size: .95rem; color: var(--muted);
  background: linear-gradient(90deg, #5E6A7D 0%, #5E6A7D 35%, #2B3FD6 48%, #7A5CFF 52%, #5E6A7D 65%, #5E6A7D 100%);
  background-size: 200% 100%; -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent; animation: shimmer 2.4s linear infinite;
}

/* ----- the trail: the steps July took ----- */
details.trail {
  background: rgba(255, 255, 255, .82); backdrop-filter: blur(6px); border: 1px solid var(--line);
  border-radius: 14px; padding: .15rem .95rem; margin: 0 0 .9rem;
}
details.trail summary { cursor: pointer; font-weight: 600; font-size: .88rem; color: var(--ink); padding: .5rem 0; list-style: none; }
details.trail summary::-webkit-details-marker { display: none; }
details.trail summary::before { content: "+"; display: inline-block; width: 1.1rem; color: var(--accent); font-weight: 700; }
details.trail[open] summary::before { content: "\\2212"; }
details.trail ol { list-style: none; counter-reset: step; margin: .1rem 0 .6rem; padding: 0; position: relative; }
details.trail ol::before { content: ""; position: absolute; left: .8rem; top: .9rem; bottom: .9rem; width: 1px; background: linear-gradient(var(--accent), var(--cyan)); opacity: .45; }
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
.st-key-approval {
  background: rgba(255, 247, 226, .92); border: 1px solid var(--amber-line); border-left: 4px solid #E0A526;
  border-radius: 14px; padding: 1rem 1.1rem 1.1rem; margin: .6rem 0 1rem; box-shadow: 0 10px 34px rgba(224, 165, 38, .14);
}
.ap-title { font-family: 'Bricolage Grotesque', system-ui, sans-serif; font-weight: 700; font-size: 1.2rem; color: #5E3F08; }
.ap-copy { color: #6B5520; font-size: .9rem; margin: .2rem 0 .3rem; }
.st-key-approval pre { white-space: pre-wrap !important; word-break: break-word; background: var(--surface) !important; border: 1px solid var(--amber-line); border-radius: 10px; }
[data-testid="stImage"] img { border-radius: 14px; border: 1px solid var(--line); }
code, pre { font-family: 'JetBrains Mono', ui-monospace, Consolas, monospace !important; }

/* ----- input: glows when you type ----- */
[data-testid="stBottom"], [data-testid="stBottom"] > div { background: transparent !important; }
[data-testid="stChatInput"] {
  background: rgba(255, 255, 255, .92); border: 1px solid var(--line); border-radius: 18px;
  box-shadow: 0 10px 40px rgba(19, 28, 43, .07); transition: box-shadow .25s, border-color .25s;
}
[data-testid="stChatInput"]:focus-within {
  border-color: transparent;
  background: linear-gradient(#fff, #fff) padding-box, linear-gradient(110deg, #2B3FD6, #7A5CFF, #22D3EE) border-box;
  box-shadow: 0 10px 44px rgba(86, 100, 255, .26);
}
[data-testid="stChatInput"] > div { background: transparent !important; border: none !important; border-radius: 18px; }
[data-testid="stChatInput"] textarea { color: var(--ink); }
[data-testid="stChatInputSubmitButton"]:not(:disabled) { background: linear-gradient(135deg, #2B3FD6, #7A5CFF) !important; color: #fff !important; border-radius: 12px; }

@media (max-width: 640px) { .user-msg { max-width: 95%; } .stApp .hero { padding-top: 2rem; } }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; }
  .shimmer { -webkit-text-fill-color: var(--muted); }
}
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
    "file_summary": "Summarize an uploaded file",
    "read_local_file": "Read an uploaded file",
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

PROMPTS = [  # (what the pill says, what July is asked)
    ("List my GitHub repositories", "List my GitHub repositories"),
    ("Summarize my uploaded file", "Summarize the file I uploaded"),
    ("Check my notices", "Check my notices from the last 7 days"),
    ("Show my last 5 emails", "Show my last 5 emails"),
    ("Search robotics news", "Search the web for the latest robotics news"),
    ("Chart my uploaded CSV", "Make a useful chart from the uploaded CSV file"),
]

ORB = '<i class="orb-ring"></i><i class="orb-core"></i><i class="orb-gloss"></i>'
MINI_ORB = '<i class="orb-core"></i><i class="orb-gloss"></i>'
THINKING = (
    f'<div class="thinking"><span class="mini-orb">{MINI_ORB}</span>'
    '<span class="shimmer">July is thinking</span></div>'
)


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
def clear_old_upload_workspaces():
    sessions_dir = os.path.join(core.DATA_ROOT, ".sessions")
    if not os.path.isdir(sessions_dir):
        return
    for name in os.listdir(sessions_dir):
        workspace = os.path.join(sessions_dir, name)
        if os.path.isdir(workspace):
            shutil.rmtree(workspace)


def new_chat():
    old_upload_dir = st.session_state.get("upload_dir")
    if old_upload_dir:
        core.clear_data_files(old_upload_dir)
    upload_dir = os.path.join(core.DATA_ROOT, ".sessions", uuid.uuid4().hex)
    core.configure_data_dir(upload_dir)
    st.session_state.upload_dir = upload_dir
    st.session_state.pop("uploaded_files", None)
    st.session_state.pop("queued", None)
    st.session_state.agent = core.JulyAgent()
    st.session_state.chat = []  # each item: role, content, tools, images


if "agent" not in st.session_state:
    # Remove legacy files from the old shared workspace before starting an isolated chat.
    core.clear_data_files(core.DATA_ROOT)
    clear_old_upload_workspaces()
    new_chat()

agent = st.session_state.agent


st.markdown("#### Add files for July to analyse")
uploaded_files = st.file_uploader(
    "Upload one or more files",
    accept_multiple_files=False,
    key="uploaded_files",
    label_visibility="collapsed",
)
if uploaded_files:
    try:
        core.clear_data_files()
        saved_name = core.save_uploaded_file(
            uploaded_files.name, uploaded_files.getvalue()
        )
    except (OSError, ValueError) as error:
        st.error(f"Could not save {uploaded_files.name}: {error}")
        saved_name = None
    if saved_name:
        st.caption("Available to July: " + saved_name)
        if st.button("Summarize uploaded files", key="summarize_uploads"):
            st.session_state.queued = (
                "Summarize every uploaded file currently available. "
                "Use the appropriate tool for each file and clearly label each result."
            )
            st.rerun()


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


def while_thinking(function, *args):
    """Show the animated 'thinking' indicator while July works."""
    slot = st.empty()
    slot.markdown(THINKING, unsafe_allow_html=True)
    try:
        return function(*args)
    finally:
        slot.empty()


# ---------- TOP BAR ----------
has_chat = bool(st.session_state.chat) or bool(agent.pending)
brand_col, action_col = st.columns([4, 1])
brand_col.markdown('<div class="brand">July<span class="sun"></span></div>', unsafe_allow_html=True)
if has_chat and action_col.button("New chat", key="new_chat"):
    new_chat()
    st.rerun()


# ---------- MAIN ----------
queued = st.session_state.pop("queued", None)  # a starter prompt that was clicked

hero_slot = st.empty()  # the start screen lives here, so it can be cleared when a message is sent
if not has_chat and not queued:
    with hero_slot.container():
        st.markdown(
            f'<div class="hero"><div class="orb">{ORB}</div>'
            f"<h1>{greeting()}.</h1><p>What should we work on?</p></div>",
            unsafe_allow_html=True,
        )
        with st.container(key="starters"):
            for i, (label, ask_text) in enumerate(PROMPTS):
                if st.button(label, key=f"prompt_{i}"):
                    st.session_state.queued = ask_text
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
        left, right, _ = st.columns([1, 1, 2.4])
        if left.button(go_label, key="approve_btn", type="primary"):
            finish_turn(while_thinking(agent.decide, True))
            st.rerun()
        if right.button("Cancel", key="reject_btn"):
            finish_turn(while_thinking(agent.decide, False))
            st.rerun()

# ----- input -----
typed = st.chat_input(
    "Choose an option above to continue." if agent.pending else "Message July",
    disabled=bool(agent.pending),
)
text = queued or typed
if text and not agent.pending:
    hero_slot.empty()
    user_item = {"role": "user", "content": text}
    st.session_state.chat.append(user_item)
    render_message(user_item)
    finish_turn(while_thinking(safe_ask, text))
    st.rerun()