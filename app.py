import asyncio
import os
import time
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("GROQ_API_KEY") and "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

if not os.getenv("OPENAI_AGENTS_DISABLE_TRACING"):
    os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = st.secrets.get(
        "OPENAI_AGENTS_DISABLE_TRACING",
        "1",
    )

from custom_agents.orchestrator import run_pipeline


def run_async(coro):
    """Run an async coroutine safely inside Streamlit."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def has_api_key() -> bool:
    key = os.getenv("GROQ_API_KEY", "")
    return bool(key and key != "your_groq_api_key_here")


st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🤖",
    layout="wide",
)

with st.sidebar:
    st.title("🤖 AI Research Assistant")

    st.markdown(
        """
### Multi-Agent Pipeline

This application uses multiple AI agents working together:

- 🔎 **Researcher**
- 📊 **Analyst**
- ✍️ **Writer**
- ✅ **Judge**

---

### Tech Stack

- Python
- OpenAI Agents SDK
- Groq Llama 3
- Streamlit
"""
    )

    if not has_api_key():
        st.error("GROQ_API_KEY is not configured.")
        st.markdown(
            """
**Local:** create a `.env` file with your key.

**Streamlit Cloud:** add `GROQ_API_KEY` in app Secrets.
"""
        )

st.title("🤖 Multi-Agent AI Research Assistant")

st.write(
    """
Generate your research reports using a multi-agent AI workflow.

The system automatically:

- 🔎 Researches the topic
- 📊 Extracts insights
- ✍️ Writes a structured report
- ✅ Reviews the report for quality
"""
)

st.divider()

with st.form("research_form"):
    topic = st.text_input(
        "Research Topic",
        placeholder="Example: Quantum Computing Applications",
    )
    submitted = st.form_submit_button(
        "🚀 Generate Report",
        disabled=not has_api_key(),
    )

if submitted:
    topic = topic.strip()

    if len(topic) < 3:
        st.warning("Please enter a valid research topic (at least 3 characters).")
    else:
        progress = st.progress(0, text="Starting pipeline...")
        status = st.empty()

        try:
            start_time = time.time()

            status.info("Running Researcher → Analyst → Writer → Judge...")
            progress.progress(10, text="Researching topic...")

            report = run_async(run_pipeline(topic))

            elapsed = time.time() - start_time
            progress.progress(100, text="Complete")
            status.empty()

            st.success(f"Report generated successfully in {elapsed:.1f} seconds.")

            st.divider()

            with st.expander("📄 View Research Report", expanded=True):
                st.markdown(report)

            filename = f"{topic.replace(' ', '_')}.md"

            st.download_button(
                "⬇️ Download Markdown Report",
                report,
                file_name=filename,
                mime="text/markdown",
            )

            try:
                reports_dir = Path("reports")
                reports_dir.mkdir(exist_ok=True)
                filepath = reports_dir / filename
                filepath.write_text(report, encoding="utf-8")
                st.caption(f"Report saved locally to `{filepath}`")
            except OSError:
                pass

        except Exception as e:
            progress.empty()
            status.empty()
            st.error(f"Pipeline failed:\n\n{e}")
            st.info(
                "If this is a rate limit error, wait a moment and try again."
            )

st.divider()

col1, col2, col3 = st.columns(3)

col1.metric("Agents", "4")
col2.metric("Pipeline", "Research → Analysis → Writing → Review")
col3.metric("Output", "Markdown Report")

st.caption("Built with Python, OpenAI Agents SDK, Groq, and Streamlit.")
