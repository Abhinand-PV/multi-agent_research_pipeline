"""
Streamlit web UI for the Multi-Agent Research Pipeline.

Entry point for Streamlit Cloud deployment and local web use.
"""

import asyncio
import logging
import os
import re
import time
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Environment setup (must happen before importing custom_agents)
# ---------------------------------------------------------------------------

load_dotenv()

# Streamlit Cloud: pull secrets into os.environ if not already set
if not os.getenv("GROQ_API_KEY") and "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

if not os.getenv("GROQ_MODEL") and "GROQ_MODEL" in st.secrets:
    os.environ["GROQ_MODEL"] = st.secrets["GROQ_MODEL"]

if not os.getenv("OPENAI_AGENTS_DISABLE_TRACING"):
    os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = st.secrets.get(
        "OPENAI_AGENTS_DISABLE_TRACING", "1"
    )

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Local imports (after env vars are set)
# ---------------------------------------------------------------------------

from custom_agents.orchestrator import run_pipeline  # noqa: E402
from custom_agents.config import GROQ_MODEL           # noqa: E402

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_async(coro):
    """Run an async coroutine safely inside Streamlit's synchronous context."""
    try:
        return asyncio.run(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()


def has_api_key() -> bool:
    """Return True if a valid GROQ_API_KEY is configured."""
    key = os.getenv("GROQ_API_KEY", "")
    return bool(key and key != "your_groq_api_key_here")


def sanitize_filename(text: str, max_length: int = 60) -> str:
    """
    Convert a topic string into a safe filename.

    Removes characters that are illegal on Windows/macOS/Linux,
    collapses whitespace, and truncates to max_length characters.
    """
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", text)
    cleaned = re.sub(r"\s+", "_", cleaned.strip())
    return cleaned[:max_length] or "report"


# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------

if "reports" not in st.session_state:
    st.session_state.reports = []  # list of {"topic": str, "content": str, "elapsed": float}

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("🤖 AI Research Assistant")

    st.markdown(
        """
### Multi-Agent Pipeline

This application uses four AI agents working in sequence:

| Stage | Agent | Role |
|---|---|---|
| 1 | 🔎 Researcher | Real web search & fact collection |
| 2 | 📊 Analyst | Insight extraction & trend analysis |
| 3 | ✍️ Writer | Professional report composition |
| 4 | ✅ Judge | Quality review & revision loop |

---

### Tech Stack

- **Python 3.10+**
- **OpenAI Agents SDK**
- **Groq** LLaMA inference
- **DuckDuckGo Search**
- **Streamlit**
"""
    )

    st.divider()

    # Model info
    st.caption(f"🧠 Model: `{GROQ_MODEL}`")

    if not has_api_key():
        st.error("⚠️ GROQ_API_KEY is not configured.")
        st.markdown(
            """
**Local:** Create a `.env` file:
```
GROQ_API_KEY=your_key_here
```

**Streamlit Cloud:** Add `GROQ_API_KEY` in **Settings → Secrets**.
"""
        )

    # Past reports in this session
    if st.session_state.reports:
        st.divider()
        st.markdown("### 📚 Session Reports")
        for i, r in enumerate(reversed(st.session_state.reports)):
            label = f"#{len(st.session_state.reports) - i} — {r['topic'][:30]}"
            if st.button(label, key=f"hist_{i}", use_container_width=True):
                st.session_state.view_report_index = len(st.session_state.reports) - 1 - i

# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------

st.title("🤖 Multi-Agent AI Research Assistant")

st.markdown(
    """
Generate in-depth, peer-reviewed research reports on any topic using a 
four-stage AI pipeline backed by **real web search**.

The pipeline automatically **researches → analyses → writes → reviews** until 
the report meets the quality threshold.
"""
)

st.divider()

# ---------------------------------------------------------------------------
# Input form
# ---------------------------------------------------------------------------

with st.form("research_form"):
    topic = st.text_input(
        "Research Topic",
        placeholder="e.g. Quantum Computing Applications in Drug Discovery",
        help="Enter any topic. The more specific, the better the report.",
    )
    col_btn, col_note = st.columns([1, 3])
    with col_btn:
        submitted = st.form_submit_button(
            "🚀 Generate Report",
            disabled=not has_api_key(),
            use_container_width=True,
        )
    with col_note:
        st.caption("Typical runtime: 30–90 seconds depending on topic complexity.")

# ---------------------------------------------------------------------------
# Pipeline execution
# ---------------------------------------------------------------------------

if submitted:
    topic = topic.strip()

    if len(topic) < 3:
        st.warning("⚠️ Please enter a valid research topic (at least 3 characters).")
    else:
        # Progress UI elements
        progress_bar = st.progress(0, text="Initialising pipeline...")
        status_box = st.empty()

        def update_progress(message: str, pct: int) -> None:
            """Callback to update Streamlit progress from inside the pipeline."""
            progress_bar.progress(pct, text=message)
            status_box.info(message)

        try:
            start_time = time.time()
            logger.info("Starting pipeline for topic: '%s'", topic)

            report = run_async(run_pipeline(topic, progress_callback=update_progress))

            elapsed = time.time() - start_time
            progress_bar.progress(100, text="✅ Complete")
            status_box.empty()

            # Persist to session history
            st.session_state.reports.append(
                {"topic": topic, "content": report, "elapsed": elapsed}
            )

            st.success(f"✅ Report generated in **{elapsed:.1f} seconds**.")

            logger.info("Pipeline completed in %.1f seconds.", elapsed)

        except Exception as exc:
            progress_bar.empty()
            status_box.empty()
            logger.exception("Pipeline failed for topic '%s'.", topic)
            st.error(f"❌ Pipeline failed:\n\n```\n{exc}\n```")
            st.info(
                "💡 If this is a rate limit error, wait 30–60 seconds and try again. "
                "If the problem persists, check your `GROQ_API_KEY`."
            )

# ---------------------------------------------------------------------------
# Report display
# ---------------------------------------------------------------------------

# Determine which report to show
view_index = getattr(st.session_state, "view_report_index", None)

if st.session_state.reports:
    if view_index is None:
        view_index = len(st.session_state.reports) - 1

    view_index = max(0, min(view_index, len(st.session_state.reports) - 1))
    current = st.session_state.reports[view_index]

    st.divider()

    col_title, col_time = st.columns([3, 1])
    with col_title:
        st.subheader(f"📄 {current['topic']}")
    with col_time:
        st.caption(f"Generated in {current['elapsed']:.1f}s")

    with st.expander("View Full Report", expanded=True):
        st.markdown(current["content"])

    # Download
    safe_name = sanitize_filename(current["topic"])
    filename = f"{safe_name}.md"

    st.download_button(
        label="⬇️ Download Markdown Report",
        data=current["content"],
        file_name=filename,
        mime="text/markdown",
        use_container_width=False,
    )

    # Save locally
    try:
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        filepath = reports_dir / filename
        filepath.write_text(current["content"], encoding="utf-8")
        st.caption(f"💾 Saved locally: `{filepath}`")
    except OSError:
        pass

# ---------------------------------------------------------------------------
# Footer metrics
# ---------------------------------------------------------------------------

st.divider()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Agents", "4", help="Researcher · Analyst · Writer · Judge")
col2.metric("Search", "DuckDuckGo", help="Real-time web search, no API key required")
col3.metric("Quality Loop", f"Up to 2 revisions", help="Judge scores each report 1–5")
col4.metric("Output", "Markdown", help="Download or copy the report")

st.caption(
    "Built with Python · OpenAI Agents SDK · Groq · DuckDuckGo Search · Streamlit"
)
