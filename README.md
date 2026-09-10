# MechAI Copilot

## Agentic AI for Industrial Fault Diagnosis & Control Engineering

MechAI Copilot is a software-based Agentic AI platform for Mechatronics
and Control Engineering. It analyzes industrial equipment sensor data
(temperature, vibration, motor current) and control-loop signals (speed
status, overshoot, oscillation), then coordinates multiple specialized
AI agents to produce fault diagnosis, control analysis, maintenance
recommendations, risk assessment, and a final synthesized engineering
report.

## Features

- Multi-Agent AI System
- Supervisor Agent (dynamically selects which specialist agents run)
- Data Analysis Agent
- Fault Diagnosis Agent
- Control Engineering Agent
- Maintenance Agent
- Risk Assessment Agent
- Final Engineering Report
- AI Engineering Chat
- Industrial Failure Simulation (5 scenarios)
- Sensor Trend Visualization
- Equipment Health Score
- Risk Assessment
- Groq AI Integration

## Technologies

- Python
- Groq API
- openai/gpt-oss-120b
- Agentic AI
- Streamlit
- Pandas
- NumPy
- Plotly

## Architecture

```
SENSOR DATA
    ↓
ENGINEERING TOOLS (deterministic health score + risk calc)
    ↓
AI AGENTS (Groq / openai/gpt-oss-120b)
    ↓
FINAL ENGINEERING REPORT
```

```
USER INPUT
    ↓
SUPERVISOR AGENT
    ↓
AGENT SELECTION
    ↓
DATA AGENT · FAULT AGENT · CONTROL AGENT · MAINTENANCE AGENT · RISK AGENT
    ↓
FINAL REPORT AGENT
    ↓
ENGINEERING REPORT
```

Deterministic engineering calculations (`engineering_tools.py`) always run
first and are never replaced by the AI — the AI agents reason over the
health score and risk level that the deterministic tools compute.

## Project Structure

```
MechAI-Copilot/
│
├── app.py                  # Streamlit UI
├── agent_system.py         # Groq-powered multi-agent orchestration
├── engineering_tools.py    # Deterministic engineering calculations
├── prompts.py               # System prompts for every agent
├── simulation.py            # Software-only failure simulation
├── requirements.txt
├── README.md
├── .gitignore
│
└── .streamlit/
    └── secrets.toml
```

## Setup

### 1. Clone and install dependencies

```bash
git clone <your-repo-url>
cd MechAI-Copilot
pip install -r requirements.txt
```

### 2. Configure your Groq API key

Get a free API key at [console.groq.com](https://console.groq.com), then
create `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "your_actual_groq_api_key_here"
```

**Never commit this file** — it is already listed in `.gitignore`.

### 3. Run locally

```bash
streamlit run app.py
```

## Deployment (Streamlit Cloud)

1. Push this repository to GitHub (secrets.toml is excluded automatically).
2. Go to [share.streamlit.io](https://share.streamlit.io) and create a new app
   pointing at `app.py`.
3. In the app's **Settings → Secrets**, add:
   ```toml
   GROQ_API_KEY = "your_actual_groq_api_key_here"
   ```
4. Deploy.

## Testing the 5 Simulation Scenarios

In the sidebar, choose **Failure Simulation**, then select each mode and
click **Generate Simulation Data** followed by **RUN AGENTIC AI ANALYSIS**:

1. **Normal** — stable readings, low risk.
2. **Bearing Failure** — rising vibration and temperature over time.
3. **Overload** — sharp rise in current and temperature.
4. **Control Instability** — oscillating vibration/current, pair with
   Speed Status = Unstable and Oscillation = Yes for full effect.
5. **Critical Failure** — steep rise across all sensors, high risk.

## Notes

- This project is 100% software-based; no hardware is required.
- The multi-agent architecture is preserved in full — Groq replaces only
  the underlying AI provider that previously was Google Gemini.
