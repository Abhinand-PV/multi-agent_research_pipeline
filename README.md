<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/OpenAI_Agents_SDK-0.17.7-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI Agents SDK">
  <img src="https://img.shields.io/badge/Groq-LLaMA_3.1--8B-F55036?style=for-the-badge&logo=meta&logoColor=white" alt="Groq">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

# Multi-Agent Research Pipeline

> An AI-powered research pipeline that orchestrates four specialized agents to automatically generate high-quality, peer-reviewed research reports on any topic — built with the **OpenAI Agents SDK** and **Groq**.

**Live Demo:** [multi-agentresearch-byabhinandpv.streamlit.app](https://multi-agentresearch-byabhinandpv.streamlit.app/)

---

## Key Features

- **Four Specialized Agents** — Each agent has a distinct role: research, analysis, writing, and quality review.
- **Automated Quality Loop** — A Judge agent scores reports and triggers revisions until a quality threshold is met.
- **Retry & Error Handling** — Built-in retry logic with exponential backoff for API rate limits and transient failures.
- **Output Validation** — Every stage validates its output for API errors, stack traces, and hallucinated content.
- **Inference Efficiency** — Powered by Groq's low-latency LLaMA 3.1-8B inference API.

---

## Screenshots & Demo

Try the deployed app: **[https://multi-agentresearch-byabhinandpv.streamlit.app/](https://multi-agentresearch-byabhinandpv.streamlit.app/)**

### Streamlit Web UI

| Home | Topic entered |
|:---:|:---:|
| ![Streamlit home page](docs/screenshots/streamlit-home.png) | ![Streamlit form filled](docs/screenshots/streamlit-form-filled.png) |

| Pipeline running | Generated report |
|:---:|:---:|
| ![Streamlit generating report](docs/screenshots/streamlit-generating.png) | ![Streamlit report result](docs/screenshots/streamlit-report-result.png) |

### Command Line Interface

**Setup verification** (`python test_setup.py`):

![CLI test setup output](docs/screenshots/cli-test-setup.png)

**Full pipeline** (`python main.py "renewable energy"`):

![CLI pipeline output](docs/screenshots/cli-pipeline.png)

### Verified features

| Feature | Status | Notes |
|---|---|---|
| Groq API connectivity | Passed | `test_setup.py` confirms agent responds |
| Multi-agent pipeline (CLI) | Passed | Research → Analysis → Writing → Judge in ~4s |
| Streamlit web UI | Passed | Topic input, report generation, markdown download |
| Judge quality loop | Passed | Report scored and approved by Judge agent |
| Live deployment | Active | Hosted on Streamlit Community Cloud |

---

## Architecture

```
                        ┌──────────────┐
                        │  User Input  │
                        │   (Topic)    │
                        └──────┬───────┘
                               │
                        ┌──────▼───────┐
                        │ Orchestrator │
                        └──────┬───────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
       ┌──────▼──────┐ ┌──────▼──────┐ ┌───────▼──────┐
       │  Researcher  │ │   Analyst   │ │    Writer    │
       │              │─▶             │─▶              │
       │ (Stage 1)    │ │  (Stage 2)  │ │  (Stage 3)   │
       └──────────────┘ └─────────────┘ └───────┬──────┘
                                                │
                                         ┌──────▼──────┐
                                         │    Judge    │
                                         │  (Stage 4)  │
                                         └──────┬──────┘
                                                │
                                    ┌───────────┴───────────┐
                                    │                       │
                              Score ≥ 4.0             Score < 4.0
                                    │                       │
                             ┌──────▼──────┐    ┌───────────▼──────────┐
                             │   Approved  │    │  Revision Required   │
                             │   Report    │    │  (Back to Writer)    │
                             └─────────────┘    └──────────────────────┘
```

---

## Agent Details

| Agent | Role | Responsibilities |
|---|---|---|
| **Researcher** | Information Gathering | Uses `search_web` tool to collect data, organizes findings, preserves facts and statistics |
| **Analyst** | Insight Extraction | Identifies key findings, trends, opportunities, risks, and relationships between ideas |
| **Writer** | Report Composition | Converts research and analysis into a structured, professional Markdown report |
| **Judge** | Quality Assurance | Scores the report on 6 criteria (1–5 scale), triggers revisions if average < 4.0 |

### Judge Evaluation Criteria

The Judge agent scores each report on the following dimensions:

| Criterion | What It Measures |
|---|---|
| **Relevance** | Does the report answer the requested topic? |
| **Completeness** | Are all important ideas covered? |
| **Accuracy** | Is the content consistent with the research? |
| **Clarity** | Is the report easy to understand? |
| **Organization** | Is the structure logical and well-formatted? |
| **Professionalism** | Would this be acceptable in a workplace setting? |

Reports scoring **≥ 4.0 average** are approved. Otherwise, the Writer receives the feedback and revises (up to **2 revision cycles**).

---

## Project Structure

```
multi-agent_research_pipeline/
├── app.py                           # Streamlit web UI (deploy entry point)
├── main.py                          # CLI entry point — accepts topic & runs pipeline
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variable template
├── .streamlit/
│   ├── config.toml                  # Streamlit theme and server settings
│   └── secrets.toml.example         # Secrets template for Streamlit Cloud
├── .gitignore                       # Git ignore rules
├── test_setup.py                    # Quick test to verify Groq connectivity
├── docs/
│   └── screenshots/                 # README screenshots (Streamlit + CLI)
├── scripts/
│   ├── capture_screenshots.py       # Capture live app screenshots
│   └── render_cli_screenshots.py    # Render CLI output for README
│
└── custom_agents/                   # Agent definitions
    ├── __init__.py
    ├── config.py                    # Groq model configuration
    ├── orchestrator.py              # Pipeline orchestration & retry logic
    ├── researcher.py                # Researcher agent + search_web tool
    ├── analyst.py                   # Analyst agent
    ├── writer.py                    # Writer agent
    └── judge.py                     # Judge agent (quality reviewer)
```

---

## Getting Started

### Prerequisites & Required Tools

To run or recreate this project, you will need the following tools, libraries, and accounts:

1. **Git**: Required for version control and cloning the repository.
2. **Python 3.10+**: The core programming language runtime environment.
3. **pip**: Python package installer (typically bundled with Python installations) to install the project packages.
4. **venv** (Python virtual environment): Recommended to isolate project dependencies.
5. **Groq API Account & Key**: Needed to access the LLaMA 3.1-8B inference API. Get a free key at [console.groq.com](https://console.groq.com).
6. **OpenAI Agents SDK (v0.17.7)**: The agent-orchestration library used to define, coordinate, and execute the multi-agent system.
7. **Streamlit (v1.32.0+)**: The frontend framework used to build and serve the interactive web interface.

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Abhinand-PV/multi-agent_research_pipeline.git
cd multi-agent_research_pipeline

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Or venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Open .env and add your GROQ_API_KEY
```

### Configuration

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
OPENAI_AGENTS_DISABLE_TRACING=1
```

---

## Usage

### Web UI (Streamlit)

Run the interactive web app locally:

```bash
streamlit run app.py
```

### Command Line Interface

```bash
python main.py "artificial intelligence in healthcare"
```

### Verify setup

```bash
python test_setup.py
```

---

## Streamlit Cloud Deployment

This project is ready to deploy on [Streamlit Community Cloud](https://share.streamlit.io).

### 1. Push to GitHub

Ensure your repository is on GitHub and includes `app.py`, `requirements.txt`, and necessary config files.

### 2. Create the app on Streamlit Cloud

1. Sign in at [share.streamlit.io](https://share.streamlit.io)
2. Click **Create app**
3. Select your GitHub repository and branch
4. Set **Main file path** to `app.py`
5. Click **Deploy**

### 3. Add secrets

In your app's **Settings → Secrets**, add:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
OPENAI_AGENTS_DISABLE_TRACING = "1"
```

### 4. Redeploy

After changing secrets or code, redeploy from the Streamlit Cloud dashboard.

---

## Configuration Options

The pipeline behavior can be tuned via constants in [`orchestrator.py`](custom_agents/orchestrator.py):

| Parameter | Default | Description |
|---|---|---|
| `MAX_RETRIES` | `3` | Maximum retry attempts per agent on transient errors |
| `MAX_REVISIONS` | `2` | Maximum revision cycles for the Writer based on Judge feedback |
| `QUALITY_THRESHOLD` | `4.0` | Minimum average score (out of 5) required for the Judge to approve |

---

## Tech Stack

| Technology | Purpose |
|---|---|
| [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) `v0.17.7` | Agent orchestration framework |
| [Groq API](https://groq.com) | Ultra-fast LLaMA 3.1-8B model inference |
| [python-dotenv](https://pypi.org/project/python-dotenv/) `v1.1.0` | Environment variable management |
| [Streamlit](https://streamlit.io) | Web UI and cloud deployment |
| Python 3.10+ | Runtime |

---

## Roadmap

- [ ] Integrate a real search provider (Tavily, SerpAPI, Brave Search)
- [ ] Add support for multiple LLM providers (OpenAI, Anthropic, Gemini)
- [ ] Export reports to PDF / HTML
- [x] Add a web-based UI for interactive use
- [ ] Implement persistent report storage
- [ ] Add citation verification and fact-checking

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built using the OpenAI Agents SDK and Groq
</p>
