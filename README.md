<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/OpenAI_Agents_SDK-0.17.7-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI Agents SDK">
  <img src="https://img.shields.io/badge/Groq-LLaMA_3.1--8B-F55036?style=for-the-badge&logo=meta&logoColor=white" alt="Groq">
  <img src="https://img.shields.io/badge/Search-DuckDuckGo-DE5833?style=for-the-badge&logo=duckduckgo&logoColor=white" alt="DuckDuckGo">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

# Multi-Agent Research Pipeline

> An autonomous, AI-powered research pipeline orchestrating specialized autonomous agents to generate high-quality, peer-reviewed research reports. Built with the **OpenAI Agents SDK** and **Groq** for high-throughput, low-latency LLM inference.

**Live Deployment:** [multi-agentresearch-byabhinandpv.streamlit.app](https://multi-agentresearch-byabhinandpv.streamlit.app/)

---

## Key Features

- 🧠 **Multi-Agent Orchestration**: Specialized agents for Research, Analysis, Writing, and QA.
- ⚡ **High-Performance Inference**: Powered by Groq and LLaMA for near-instant text generation.
- 🔄 **Self-Correcting Pipeline**: Automated quality evaluation and revision loops.
- 🌐 **Real-Time Web Data**: Integrates directly with DuckDuckGo for up-to-date information.
- 📊 **Interactive GUI**: User-friendly Streamlit interface for effortless interaction.

---

## Technical Overview

This project implements a multi-agent system designed to handle complex research tasks through distributed responsibilities. By isolating concerns across four specialized agents—Research, Analysis, Writing, and Quality Assurance—the system minimizes hallucination and maximizes output quality. The architecture features an automated quality-control loop, deterministic output validation, and exponential backoff for fault tolerance.

### Core Architecture

- **Separation of Concerns**: Four distinct AI agents operate in a sequential pipeline, each optimized with specific system instructions and tuned LLM sampling parameters (temperature) appropriate for their function.
- **Automated Feedback Loop**: A programmatic Judge agent evaluates the final output against structured criteria, capable of triggering multiple revision cycles back to the Writer agent if the quality threshold is not met.
- **Fault Tolerance**: Robust retry mechanisms with exponential backoff handle transient API rate limits and network interruptions.
- **Strict Output Validation**: Deterministic validation layers prevent the propagation of LLM artifacts (e.g., stack traces, hallucinated tool calls) down the pipeline.
- **Real-Time Data Integration**: Integrates directly with DuckDuckGo for live web data, bypassing the need for static or pre-trained knowledge retrieval.

---

## System Architecture

```text
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
       │  (Web API)   │─▶  Insights  │─▶   Report    │
       │  (Stage 1)   │ │  (Stage 2)  │ │  (Stage 3)   │
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
                                                (up to N revision cycles)
```

---

## Agent Specifications

Each agent in the system is configured with a specific role, instruction set, and sampling temperature to optimize for either determinism or creativity.

| Agent | Role | Sub-system Responsibilities | LLM Temp |
|---|---|---|---|
| **Researcher** | Information Retrieval | Executes targeted queries via DuckDuckGo API, deduplicates sources, and structures raw findings. | `0.2` |
| **Analyst** | Insight Extraction | Synthesizes raw data, identifying macro trends, correlative insights, and potential data gaps. | `0.2` |
| **Writer** | Report Composition | Transforms analytical insights into a structured, professional Markdown document. | `0.5` |
| **Judge** | Quality Assurance | Scores the output on 6 predefined dimensions (1-5 scale) and provides programmatic feedback. | `0.1` |

### Automated Quality Assurance (Judge Agent)

The Judge agent enforces a strict evaluation matrix before output delivery:
1. **Relevance**: Alignment with the initial user prompt.
2. **Completeness**: Coverage of required analytical dimensions.
3. **Accuracy**: Consistency with the retrieved ground-truth data.
4. **Clarity**: Lexical precision and readability.
5. **Organization**: Structural integrity of the Markdown document.
6. **Professionalism**: Suitability for enterprise or academic consumption.

Reports must achieve a minimum composite score of **4.0/5.0**. Sub-standard reports trigger a feedback loop, routing the Judge's specific critiques back to the Writer for iterative refinement.

---

## Technology Stack

- **OpenAI Agents SDK (`v0.17.7`)**: Core orchestration framework for agent lifecycle management.
- **Groq API**: High-speed LLaMA inference engine powering the LLM backend.
- **DuckDuckGo Search (`≥6.2.0`)**: Real-time web data retrieval.
- **Streamlit (`≥1.32.0`)**: Interactive web interface with session state management.
- **Python (`3.10+`)**: Primary runtime environment.

---

## Interface Options

### Streamlit Web Interface

Provides a full GUI with real-time pipeline telemetry, session state persistence for historical reports, and integrated document download capabilities.

```bash
streamlit run app.py
```

### Command Line Interface (CLI)

Designed for headless execution or integration into broader automation scripts. Features live standard output logging and stage progression tracking.

```bash
python main.py "Advances in Quantum Error Correction"
```

---

## Setup and Installation

### Prerequisites
- Python 3.10 or higher
- Git
- Groq API Key (Available at [console.groq.com](https://console.groq.com))

### Local Environment Initialization

```bash
# Clone the repository
git clone https://github.com/Abhinand-PV/multi-agent_research_pipeline.git
cd multi-agent_research_pipeline

# Initialize virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
```

### Configuration (`.env`)

```env
# Required Authorization
GROQ_API_KEY=your_groq_api_key_here

# Model Selection
# Options: llama-3.1-8b-instant (default), llama-3.3-70b-versatile
GROQ_MODEL=llama-3.1-8b-instant

# Telemetry Configuration
OPENAI_AGENTS_DISABLE_TRACING=1
```

---

## Project Structure

```text
multi-agent_research_pipeline/
├── app.py                           # Streamlit web application entry point
├── main.py                          # CLI execution entry point
├── requirements.txt                 # Project dependency specifications
├── .env.example                     # Environment variable template
├── custom_agents/                   # Agent and Orchestration Logic
│   ├── orchestrator.py              # Pipeline execution, retry logic, and event routing
│   ├── config.py                    # Global model and SDK configuration
│   ├── researcher.py                # Retrieval agent and search tool integration
│   ├── analyst.py                   # Synthesis agent definition
│   ├── writer.py                    # Composition agent definition
│   └── judge.py                     # Evaluation agent and quality criteria
```

---

## Roadmap and Future Enhancements

- **Pluggable Search Interfaces**: Abstract the search layer to support Tavily, SerpAPI, and internal vector databases.
- **Multi-Provider LLM Support**: Expand compatibility beyond Groq to support OpenAI, Anthropic, and localized models.
- **Advanced State Management**: Implement persistent storage layers (e.g., PostgreSQL, Redis) for cross-session report archiving.
- **Citation Verification**: Introduce a dedicated fact-checking agent to rigorously map claims to specific source URLs.

---

## Contributing

Contributions are always welcome! If you'd like to improve this project, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

Please ensure your code adheres to the existing style and includes appropriate documentation.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
