import streamlit as st
import asyncio
from pathlib import Path
from dotenv import load_dotenv

from custom_agents.orchestrator import run_pipeline

# Load environment variables (.env must contain GROQ_API_KEY)
load_dotenv()


def run_async(coro):
    """Run an async coroutine safely inside Streamlit."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

# ---------------------------------------------------
# Page Configuration
# ---------------------------------------------------

st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🤖",
    layout="wide",
)

# ---------------------------------------------------
# Sidebar
# ---------------------------------------------------

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

# ---------------------------------------------------
# Header
# ---------------------------------------------------

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

# ---------------------------------------------------
# Input Form
# ---------------------------------------------------

with st.form("research_form"):

    topic = st.text_input(
        "Research Topic",
        placeholder="Example: Quantum Computing Applications",
    )

    submitted = st.form_submit_button("🚀 Generate Report")

# ---------------------------------------------------
# Generate Report
# ---------------------------------------------------

if submitted:

    topic = topic.strip()

    if len(topic) < 3:
        st.warning("Please enter a valid research topic.")

    else:

        progress = st.progress(0)

        status = st.empty()

        runtime_placeholder = st.empty()

        try:

            status.write("🔎 Researching...")
            progress.progress(25)

            report = run_async(run_pipeline(topic))

            status.write("📊 Analyzing...")
            progress.progress(50)

            status.write("✍️ Writing Report...")
            progress.progress(75)

            status.write("✅ Quality Review Complete")
            progress.progress(100)

            st.success("Report generated successfully!")

            st.divider()

            with st.expander(
                "📄 View Research Report",
                expanded=True,
            ):
                st.markdown(report)

            # Save report

            Path("reports").mkdir(exist_ok=True)

            filename = topic.replace(" ", "_") + ".md"

            filepath = Path("reports") / filename

            filepath.write_text(
                report,
                encoding="utf-8",
            )

            st.download_button(
                "⬇️ Download Markdown Report",
                report,
                file_name=filename,
                mime="text/markdown",
            )

            st.info(f"Report also saved locally to:\n\n{filepath}")

        except Exception as e:

            st.error(f"Error:\n\n{e}")

# ---------------------------------------------------
# Footer
# ---------------------------------------------------

st.divider()

col1, col2, col3 = st.columns(3)

col1.metric("Agents", "4")
col2.metric("Pipeline", "Research → Analysis → Writing → Review")
col3.metric("Output", "Markdown Report")

st.caption(
    "Built Python, OpenAI Agents SDK, Groq, and Streamlit."
)