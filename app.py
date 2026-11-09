"""July in your browser. Run:  python -m streamlit run app.py"""
import ast
import html
import os
import random
import re
import time
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
    initial_sidebar_state="expanded",
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
[data-testid="stAppDeployButton"], [data-testid="stToolbarActions"], [data-testid="stMainMenu"], #MainMenu, footer { display: none !important; }
/* the button that reopens the sidebar after you close it */
[data-testid="stExpandSidebarButton"] {
  display: inline-flex !important; visibility: visible !important;
  background: rgba(255, 255, 255, .85) !important; backdrop-filter: blur(6px);
  border: 1px solid var(--line) !important; border-radius: 12px !important;
  box-shadow: 0 6px 20px rgba(19, 28, 43, .08); color: var(--accent) !important;
}
[data-testid="stExpandSidebarButton"]:hover { border-color: var(--accent) !important; box-shadow: 0 8px 26px rgba(43, 63, 214, .18); }
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

/* ----- sidebar: July's side panel ----- */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #F7F8FC 0%, #EEF1F8 100%) !important;
  border-right: 1px solid var(--line);
}
[data-testid="stSidebar"] [data-testid="stSidebarContent"] { padding-top: .4rem; }
[data-testid="stSidebarHeader"] { height: 2.2rem; min-height: 0; }

/* the presence card: a little night sky with July glowing in it */
.presence {
  position: relative; overflow: hidden; border-radius: 20px; padding: 1.4rem 1.1rem 1.1rem;
  color: #EAF0FF; text-align: center;
  background:
    radial-gradient(220px 160px at 50% 0%, rgba(122, 92, 255, .55), transparent 70%),
    radial-gradient(180px 140px at 0% 100%, rgba(34, 211, 238, .28), transparent 70%),
    linear-gradient(160deg, #141A3A 0%, #0D1226 100%);
  box-shadow: 0 18px 40px rgba(20, 26, 58, .28), inset 0 1px 0 rgba(255, 255, 255, .08);
}
.presence::before {   /* tiny stars */
  content: ""; position: absolute; inset: 0; pointer-events: none; opacity: .55;
  background-image:
    radial-gradient(1px 1px at 18% 22%, #fff, transparent), radial-gradient(1px 1px at 78% 18%, #fff, transparent),
    radial-gradient(1px 1px at 62% 64%, #fff, transparent), radial-gradient(1px 1px at 30% 78%, #fff, transparent),
    radial-gradient(1.5px 1.5px at 88% 52%, #fff, transparent), radial-gradient(1px 1px at 10% 58%, #fff, transparent);
  animation: twinkle 5s ease-in-out infinite alternate;
}
@keyframes twinkle { to { opacity: .2; } }
.presence .orb { width: 72px; height: 72px; margin: 0 auto .9rem; }
.presence .orb-ring { border-color: rgba(160, 175, 255, .45); border-top-color: transparent; border-left-color: transparent; }
.p-name { font-family: 'Bricolage Grotesque', system-ui, sans-serif; font-weight: 700; font-size: 1.5rem; letter-spacing: -.035em; line-height: 1; }
.p-status { display: inline-flex; align-items: center; gap: .4rem; margin-top: .5rem; font-size: .78rem; color: #B9C3E6; }
.p-status i { width: .5rem; height: .5rem; border-radius: 50%; background: #3BE48A; box-shadow: 0 0 0 0 rgba(59, 228, 138, .6); animation: pulse 2s infinite; }
@keyframes pulse { 70% { box-shadow: 0 0 0 7px rgba(59, 228, 138, 0); } 100% { box-shadow: 0 0 0 0 rgba(59, 228, 138, 0); } }
.p-doing {
  margin-top: .9rem; padding: .55rem .7rem; border-radius: 12px; font-size: .8rem; line-height: 1.4;
  background: rgba(255, 255, 255, .07); border: 1px solid rgba(255, 255, 255, .10); color: #D5DCF5; font-style: italic;
}

.side-label { font-size: .7rem; font-weight: 600; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); margin: 1.3rem 0 .5rem; }

/* this-chat stats */
.stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: .45rem; }
.stat { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: .6rem .4rem; text-align: center; }
.stat b {
  display: block; font-family: 'Bricolage Grotesque', system-ui, sans-serif; font-size: 1.35rem; line-height: 1.1;
  background: linear-gradient(135deg, #2B3FD6, #7A5CFF); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
}
.stat span { font-size: .7rem; color: var(--muted); }

/* powers: what July is plugged into */
.powers { display: grid; grid-template-columns: 1fr 1fr; gap: .45rem; }
.power { display: flex; align-items: center; gap: .5rem; background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: .5rem .6rem; font-size: .8rem; color: var(--muted); }
.power svg { width: 16px; height: 16px; flex: none; stroke: currentColor; fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.power .dot { margin-left: auto; width: .45rem; height: .45rem; border-radius: 50%; background: #C5CCD8; flex: none; }
.power.on { color: var(--ink); border-color: #CBD3FF; }
.power.on svg { stroke: var(--accent); }
.power.on .dot { background: #12A150; box-shadow: 0 0 6px rgba(18, 161, 80, .6); }

.vault { display: flex; align-items: center; gap: .55rem; margin-top: .45rem; padding: .55rem .7rem; border-radius: 12px; border: 1px dashed #C9D0DD; font-size: .78rem; color: var(--muted); }
.vault svg { width: 15px; height: 15px; flex: none; stroke: currentColor; fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }

[data-testid="stSidebar"] .stButton > button, [data-testid="stSidebar"] .stDownloadButton > button { width: 100%; }
[data-testid="stSidebar"] [data-testid="stButtonGroup"] { width: 100%; }
[data-testid="stSidebar"] [data-testid="stButtonGroup"] > div { width: 100%; }
[data-testid="stSidebar"] [data-testid="stButtonGroup"] button { flex: 1; }
.stDownloadButton > button { border-radius: 10px; font-weight: 600; border: 1px solid var(--line); background: var(--surface); color: var(--ink); }

/* ----- message extras ----- */
.stamp { font-size: .72rem; color: var(--muted); opacity: .8; margin-top: .15rem; }
.user-wrap { flex-direction: column; align-items: flex-end; }
.files { display: flex; flex-wrap: wrap; gap: .35rem; justify-content: flex-end; margin-bottom: .35rem; }
.file-chip { font-size: .78rem; font-family: 'JetBrains Mono', ui-monospace, Consolas, monospace; padding: .2rem .55rem; border-radius: 8px; background: #EEF1FF; border: 1px solid #CBD3FF; color: var(--accent-dark); }
.dots { display: inline-flex; gap: 3px; margin-left: .15rem; }
.dots i { width: 4px; height: 4px; border-radius: 50%; background: var(--accent); animation: hop 1.2s infinite ease-in-out; }
.dots i:nth-child(2) { animation-delay: .15s; } .dots i:nth-child(3) { animation-delay: .3s; }
@keyframes hop { 0%, 60%, 100% { transform: translateY(0); opacity: .4; } 30% { transform: translateY(-4px); opacity: 1; } }

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
        "Can I change this file on GitHub?",
        "Don't worry, it goes to a new branch with a pull request. Main stays untouched until you merge it.",
        "Apply change",
    ),
    "JULY WANTS TO CHANGE A CSV CELL": (
        "Okay if I edit this CSV value?",
        "I'll save a backup first, just in case.",
        "Apply change",
    ),
    "JULY WANTS TO SEND AN EMAIL": (
        "Ready to send this email?",
        "Give it a quick read. It goes out from your Gmail account.",
        "Send email",
    ),
    "JULY WANTS TO FORGET A FACT": (
        "Want me to forget this?",
        "It gets wiped from my memory for good.",
        "Forget fact",
    ),
}

PROMPTS = [  # (what the pill says, what July is asked)
    ("Hey July, how's it going?", "Hey July, how's it going?"),
    ("List my GitHub repositories", "List my GitHub repositories"),
    ("Summarize my uploaded file", "Summarize the file I uploaded"),
    ("Check my notices", "Check my notices from the last 7 days"),
    ("Show my last 5 emails", "Show my last 5 emails"),
    ("Search robotics news", "Search the web for the latest robotics news"),
    ("Tell me a nerdy joke", "Tell me a nerdy joke"),
]

ORB = '<i class="orb-ring"></i><i class="orb-core"></i><i class="orb-gloss"></i>'
MINI_ORB = '<i class="orb-core"></i><i class="orb-gloss"></i>'
THINKING_LINES = [
    "Hmm, let me think",
    "On it",
    "Give me a sec",
    "Poking around",
    "Thinking very hard (dramatically)",
    "Digging in",
    "Working my magic",
]
DECISION_LINES = {
    True: ["Okay, doing it now", "Making it happen", "Here goes"],
    False: ["No worries, scrapping that", "Cancelled, all good"],
}
SUBTITLES = [
    "What are we getting into today?",
    "I'm all ears. Well, all tokens.",
    "Got something for me, or just here to chat?",
    "Ready when you are.",
    "What's on your mind?",
]
VIBE_HELP = {
    "Playful": "Jokes and banter, still gets it done.",
    "Chill": "Relaxed and warm.",
    "Focused": "Brief, straight to results.",
}
ACCEPTED_TYPES = ["csv", "tsv", "txt", "md", "json", "pdf", "xlsx", "xls", "py", "log"]


# ---------- HELPERS ----------
def esc(text):
    return html.escape(str(text), quote=True)


def thinking_html(line=None):
    line = line or random.choice(THINKING_LINES)
    return (
        f'<div class="thinking"><span class="mini-orb">{MINI_ORB}</span>'
        f'<span class="shimmer">{esc(line)}</span>'
        '<span class="dots"><i></i><i></i><i></i></span></div>'
    )


def user_name():
    """Find the user's name in July's memory, if a fact like 'name is X' was saved."""
    for fact in core.load_memory():
        found = re.search(r"\bname is ([A-Z][a-zA-Z]+)", fact) or re.search(r"\bcalled ([A-Z][a-zA-Z]+)", fact)
        if found:
            return found.group(1)
    return None


def greeting():
    hour = datetime.now().hour
    name = user_name()
    if hour < 5:
        return f"Still up, {name}?" if name else "Still up?"
    if hour < 12:
        hello = "Good morning"
    elif hour < 18:
        hello = "Good afternoon"
    else:
        hello = "Good evening"
    return f"{hello}, {name}." if name else f"{hello}."


def stamp():
    return datetime.now().strftime("%I:%M %p").lstrip("0")


def type_out(text):
    """Yield the reply a word at a time, so July 'types' it."""
    for word in re.split(r"(\s+)", text):
        yield word
        if word.strip():
            time.sleep(0.018)


def chat_markdown():
    """The whole conversation as a Markdown file for download."""
    lines = [f"# Chat with July ({datetime.now():%d %b %Y})", ""]
    for item in st.session_state.chat:
        who = "You" if item["role"] == "user" else "July"
        lines.append(f"**{who}** ({item.get('time', '')})")
        if item.get("files"):
            lines.append("Attached: " + ", ".join(item["files"]))
        lines += [item["content"], ""]
    return "\n".join(lines)


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
        when = f'<div class="stamp">{esc(item["time"])}</div>' if item.get("time") else ""
        if item["role"] == "user":
            chips = "".join(f'<span class="file-chip">{esc(n)}</span>' for n in item.get("files", []))
            files = f'<div class="files">{chips}</div>' if chips else ""
            bubble = f'<div class="user-msg">{esc(item["content"])}</div>' if item["content"] else ""
            st.markdown(f'<div class="user-wrap">{files}{bubble}{when}</div>', unsafe_allow_html=True)
            return
        if item.get("tools"):
            st.markdown(trail_html(item["tools"]), unsafe_allow_html=True)
        for path in item.get("images", []):
            if os.path.exists(path):
                st.image(path)
        if item.pop("fresh", False):   # a brand-new reply: type it out once
            st.write_stream(type_out(item["content"]))
        else:
            st.markdown(item["content"])
        if when:
            st.markdown(when, unsafe_allow_html=True)


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
    st.session_state.agent = core.JulyAgent(st.session_state.get("vibe", core.DEFAULT_VIBE))
    st.session_state.subtitle = random.choice(SUBTITLES)
    st.session_state.chat = []  # each item: role, content, tools, images


if "agent" not in st.session_state:
    # Remove legacy files from the old shared workspace before starting an isolated chat.
    core.clear_data_files(core.DATA_ROOT)
    clear_old_upload_workspaces()
    new_chat()

agent = st.session_state.agent


def finish_turn(result):
    """If July finished answering, save the answer in the chat history."""
    if result["status"] == "done":
        tools, images = agent.take_log()
        st.session_state.chat.append(
            {
                "role": "assistant", "content": result["text"], "tools": tools,
                "images": images, "time": stamp(), "fresh": True,
            }
        )


def safe_ask(text):
    try:
        return agent.ask(text)
    except Exception as e:  # keep the page alive, and say what happened
        return {"status": "done", "text": f"Oof, I tripped over something and couldn't finish that. Details: {e}"}


def save_attachments(files):
    """Save files attached in the chat box. Returns the saved names."""
    saved = []
    if not files:
        return saved
    core.clear_data_files()   # July analyses only the newest attachments
    for f in files:
        try:
            saved.append(core.save_uploaded_file(f.name, f.getvalue()))
        except (OSError, ValueError) as error:
            st.error(f"Couldn't save {f.name}: {error}")
    return saved


def while_thinking(function, *args, line=None):
    """Show the animated 'thinking' indicator while July works."""
    slot = st.empty()
    slot.markdown(thinking_html(line), unsafe_allow_html=True)
    try:
        return function(*args)
    finally:
        slot.empty()


# ---------- SIDEBAR ----------
has_chat = bool(st.session_state.chat) or bool(agent.pending)

DOINGS = [  # a little "what July is up to" line, like a status on a messaging app
    "Currently pretending to sip coffee.",
    "Humming quietly in binary.",
    "Judging tabs vs spaces. Silently.",
    "Reorganising my thoughts alphabetically.",
    "Waiting for you to say something fun.",
    "Stretching my neural nets.",
    "Counting to infinity. Almost there.",
]
ICONS = {  # tiny line icons (stroke only, they take the text colour)
    "GitHub": '<svg viewBox="0 0 24 24"><path d="M9 19c-4 1.5-4-2-6-2.5M15 21v-3.5c0-1 .1-1.4-.5-2 2.8-.3 5.5-1.4 5.5-6a4.6 4.6 0 0 0-1.3-3.2 4.2 4.2 0 0 0-.1-3.2s-1-.3-3.4 1.3a11.5 11.5 0 0 0-6 0C6.8 2.8 5.8 3.1 5.8 3.1a4.2 4.2 0 0 0-.1 3.2A4.6 4.6 0 0 0 4.4 9.5c0 4.6 2.7 5.7 5.5 6-.6.6-.6 1.2-.5 2V21"/></svg>',
    "Edits": '<svg viewBox="0 0 24 24"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>',
    "Email": '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>',
    "Web": '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/></svg>',
}
LOCK = '<svg viewBox="0 0 24 24"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>'


def power_tile(label, on):
    return f'<div class="power{" on" if on else ""}">{ICONS[label]}{esc(label)}<span class="dot"></span></div>'


if "doing" not in st.session_state:
    st.session_state.doing = random.choice(DOINGS)

with st.sidebar:
    st.markdown(
        f'<div class="presence"><div class="orb">{ORB}</div>'
        '<div class="p-name">July</div>'
        f'<div class="p-status"><i></i>online &middot; {esc(agent.vibe.lower())} mode</div>'
        f'<div class="p-doing">{esc(st.session_state.doing)}</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="side-label">Vibe</div>', unsafe_allow_html=True)
    picked = st.segmented_control(
        "Vibe", list(core.VIBES), default=agent.vibe, key="vibe_picker", label_visibility="collapsed"
    )
    if picked and picked != agent.vibe:
        agent.vibe = st.session_state.vibe = picked
        st.rerun()
    st.caption(VIBE_HELP.get(agent.vibe, ""))

    chat = st.session_state.chat
    st.markdown('<div class="side-label">This chat</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="stats">'
        f'<div class="stat"><b>{len(chat)}</b><span>messages</span></div>'
        f'<div class="stat"><b>{sum(len(i.get("tools", [])) for i in chat)}</b><span>steps</span></div>'
        f'<div class="stat"><b>{sum(len(i.get("files", [])) for i in chat)}</b><span>files</span></div>'
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="side-label">Powers</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="powers">'
        + power_tile("GitHub", bool(core.GITHUB_TOKEN))
        + power_tile("Edits", bool(core.WRITE_REPOS))
        + power_tile("Email", bool(core.EMAIL_ADDRESS and core.EMAIL_APP_PASSWORD))
        + power_tile("Web", True)
        + "</div>"
        # memories stay private: never listed here, only July sees them
        + f'<div class="vault">{LOCK}<span>Memories are private. Ask me in chat.</span></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="side-label">&nbsp;</div>', unsafe_allow_html=True)
    if st.button("+  New chat", key="new_chat", type="primary", disabled=not has_chat):
        st.session_state.doing = random.choice(DOINGS)
        new_chat()
        st.rerun()
    if chat:
        st.download_button(
            "Download chat", chat_markdown(), file_name=f"july-chat-{datetime.now():%Y%m%d-%H%M}.md",
            mime="text/markdown", key="download_chat",
        )


# ---------- MAIN ----------
queued = st.session_state.pop("queued", None)  # a starter prompt that was clicked

hero_slot = st.empty()  # the start screen lives here, so it can be cleared when a message is sent
if not has_chat and not queued:
    with hero_slot.container():
        st.markdown(
            f'<div class="hero"><div class="orb">{ORB}</div>'
            f"<h1>{esc(greeting())}</h1><p>{esc(st.session_state.subtitle)}</p></div>",
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
            finish_turn(while_thinking(agent.decide, True, line=random.choice(DECISION_LINES[True])))
            st.rerun()
        if right.button("Cancel", key="reject_btn"):
            finish_turn(while_thinking(agent.decide, False, line=random.choice(DECISION_LINES[False])))
            st.rerun()

# ----- input (type a message, or attach files with the paperclip) -----
typed = st.chat_input(
    "Pick an option above first." if agent.pending else "Message July, or attach a file",
    disabled=bool(agent.pending),
    accept_file="multiple",
    file_type=ACCEPTED_TYPES,
)
text, shown, files = queued, queued, []
if typed:
    shown = text = (typed.text or "").strip()
    files = save_attachments(typed.files)
    if files and not text:
        text = "I just shared " + ", ".join(files) + ". Take a look and tell me what's in it."
    elif files:
        text = f"[Files just attached: {', '.join(files)}]\n{text}"
if text and not agent.pending:
    hero_slot.empty()
    user_item = {"role": "user", "content": shown, "files": files, "time": stamp()}
    st.session_state.chat.append(user_item)
    render_message(user_item)
    finish_turn(while_thinking(safe_ask, text))
    st.rerun()
