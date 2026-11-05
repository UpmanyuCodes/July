"""July in your browser. Run:  python -m streamlit run app.py"""
import os

import streamlit as st

import july_core as core

core.APPROVAL_MODE = "ui"   # approvals become buttons instead of input()

st.set_page_config(page_title="July", page_icon="🤖")


# ---------- STATE (kept while the browser tab is open) ----------
def new_chat():
    st.session_state.agent = core.JulyAgent()
    st.session_state.chat = []   # each item: role, content, tools, images


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


# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("🤖 July")
    st.caption("Your free, safe AI agent")

    if st.button("🗑️ New chat", use_container_width=True):
        new_chat()
        st.rerun()

    st.subheader("Status")
    if core.WRITE_REPOS:
        st.write("GitHub writes: " + ", ".join(sorted(core.WRITE_REPOS)))
    else:
        st.write("GitHub: read-only")
    st.write("Email: " + ("on" if core.EMAIL_ADDRESS and core.EMAIL_APP_PASSWORD else "off"))

    facts = core.load_memory()
    st.subheader(f"Memory ({len(facts)})")
    if facts:
        for fact in facts:
            st.write(f"• {fact}")
    else:
        st.caption("Nothing saved yet. Try: remember that I like Python.")

    st.divider()
    st.caption(
        "Every change (GitHub edit, CSV edit, email, forget) needs your approval. "
        "Run this app only on your own computer: it can use your Gmail and GitHub."
    )


# ---------- CHAT HISTORY ----------
st.title("July")

if not st.session_state.chat and not agent.pending:
    st.info(
        "Try: `check my notices from the last 7 days`, `list my repos`, "
        "`search the web for robotics news`, or `remember that I like Python`."
    )

for item in st.session_state.chat:
    with st.chat_message(item["role"]):
        if item.get("tools"):
            with st.expander(f"🔧 Tools used ({len(item['tools'])})"):
                for line in item["tools"]:
                    st.code(line, language=None)
        for path in item.get("images", []):
            if os.path.exists(path):
                st.image(path)
        st.markdown(item["content"])


# ---------- APPROVAL BOX (shown when July wants to change something) ----------
if agent.pending:
    p = agent.pending
    with st.chat_message("assistant"):
        st.warning(f"⚠️ {p['title']}")
        st.code("\n".join(p["lines"]), language=None)
        left, right = st.columns(2)
        if left.button("✅ Approve", use_container_width=True, type="primary"):
            with st.spinner("July is working..."):
                finish_turn(agent.decide(True))
            st.rerun()
        if right.button("❌ Reject", use_container_width=True):
            with st.spinner("July is working..."):
                finish_turn(agent.decide(False))
            st.rerun()


# ---------- INPUT ----------
prompt = st.chat_input(
    "Waiting for your approval above..." if agent.pending else "Ask July anything...",
    disabled=bool(agent.pending),
)
if prompt:
    st.session_state.chat.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.spinner("July is thinking..."):
        finish_turn(agent.ask(prompt))
    st.rerun()