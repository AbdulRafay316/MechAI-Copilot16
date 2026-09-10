"""
app.py
------
MechAI Copilot - Streamlit interface.

Agentic AI for Industrial Fault Diagnosis & Control Engineering.

Uses Groq API (GROQ_API_KEY) instead of Google Gemini. The API key is
loaded safely from Streamlit Secrets and is never hardcoded or displayed.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from agent_system import MechAIAgentSystem
from engineering_tools import run_engineering_analysis
from simulation import run_simulation, get_latest_reading, SIMULATION_MODES

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="MechAI Copilot",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ======================================================
# LOAD API KEY SAFELY FROM STREAMLIT SECRETS
# ======================================================
try:
    API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    API_KEY = None

# ======================================================
# SESSION STATE INIT
# ======================================================
if "agent_system" not in st.session_state:
    st.session_state.agent_system = MechAIAgentSystem(api_key=API_KEY)

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "engineering_result" not in st.session_state:
    st.session_state.engineering_result = None

if "sim_df" not in st.session_state:
    st.session_state.sim_df = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

agent_system = st.session_state.agent_system

# ======================================================
# LIGHT STYLING
# ======================================================
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.1rem;
        font-weight: 800;
        margin-bottom: 0;
    }
    .subtitle {
        font-size: 1.05rem;
        color: #9aa5b1;
        margin-top: 0;
        margin-bottom: 1.2rem;
    }
    .metric-card {
        border-radius: 12px;
        padding: 1rem 1.2rem;
        background: rgba(120, 130, 255, 0.08);
        border: 1px solid rgba(120, 130, 255, 0.25);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ======================================================
# HEADER
# ======================================================
st.markdown('<p class="main-title">⚙️ MechAI Copilot</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Agentic AI for Industrial Fault Diagnosis & Control Engineering</p>',
    unsafe_allow_html=True,
)

if API_KEY is None:
    st.warning(
        "⚠️ GROQ_API_KEY is not configured. Add it to `.streamlit/secrets.toml` "
        "(locally) or to your Streamlit Cloud app secrets to enable AI analysis. "
        "Deterministic engineering calculations will still work.",
        icon="⚠️",
    )

# ======================================================
# SIDEBAR — INPUT CONTROLS
# ======================================================
with st.sidebar:
    st.header("🔧 Analysis Setup")

    analysis_mode = st.radio(
        "Analysis Mode",
        ["Manual Input", "Failure Simulation"],
        help="Choose whether to enter sensor readings manually or generate a synthetic failure scenario.",
    )

    st.divider()

    if analysis_mode == "Manual Input":
        st.subheader("📟 Manual Sensor Inputs")
        temperature = st.slider("Temperature (°C)", 0.0, 150.0, 55.0, 0.5)
        vibration = st.slider("Vibration (mm/s)", 0.0, 15.0, 1.8, 0.1)
        motor_current = st.slider("Motor Current (A)", 0.0, 40.0, 9.0, 0.1)
    else:
        st.subheader("🧪 Failure Simulation Mode")
        sim_mode = st.selectbox("Simulation Scenario", SIMULATION_MODES)
        duration = st.slider("Simulation Duration (s)", 20, 120, 60, 5)
        if st.button("▶️ Generate Simulation Data", use_container_width=True):
            st.session_state.sim_df = run_simulation(sim_mode, duration_seconds=duration)

        if st.session_state.sim_df is not None:
            latest = get_latest_reading(st.session_state.sim_df)
            temperature = latest["temperature"]
            vibration = latest["vibration"]
            motor_current = latest["current"]
        else:
            temperature, vibration, motor_current = 45.0, 1.2, 8.0

    st.divider()
    st.subheader("🎛️ Control System Information")
    speed_status = st.selectbox("Speed Status", ["Stable", "Unstable"])
    overshoot = st.selectbox("Overshoot", ["Low", "Normal", "High"])
    oscillation = st.selectbox("Oscillation", ["No", "Yes"])

    st.divider()
    run_clicked = st.button("🚀 RUN AGENTIC AI ANALYSIS", type="primary", use_container_width=True)

# ======================================================
# SIMULATION CHART (if applicable)
# ======================================================
if analysis_mode == "Failure Simulation" and st.session_state.sim_df is not None:
    st.subheader("📈 Simulated Sensor Trends")
    df = st.session_state.sim_df
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Time"], y=df["Temperature"], name="Temperature (°C)", mode="lines"))
    fig.add_trace(go.Scatter(x=df["Time"], y=df["Vibration"], name="Vibration (mm/s)", mode="lines", yaxis="y2"))
    fig.add_trace(go.Scatter(x=df["Time"], y=df["Current"], name="Current (A)", mode="lines", yaxis="y3"))

    fig.update_layout(
        xaxis=dict(title="Time (s)"),
        yaxis=dict(title="Temperature (°C)"),
        yaxis2=dict(title="Vibration (mm/s)", overlaying="y", side="right"),
        yaxis3=dict(title="Current (A)", overlaying="y", side="right", anchor="free", position=1.0),
        legend=dict(orientation="h", y=1.15),
        height=380,
        margin=dict(t=30, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)

# ======================================================
# RUN ANALYSIS
# ======================================================
if run_clicked:
    with st.spinner("Running deterministic engineering analysis..."):
        eng_result = run_engineering_analysis(
            temperature=temperature,
            vibration=vibration,
            current=motor_current,
            speed_status=speed_status,
            overshoot=overshoot,
            oscillation=oscillation,
        )
        st.session_state.engineering_result = eng_result

    equipment_context = f"""
SENSOR DATA:
- Temperature: {temperature} °C ({eng_result['temperature']['status']})
- Vibration: {vibration} mm/s ({eng_result['vibration']['status']})
- Motor Current: {motor_current} A ({eng_result['current']['status']})

CONTROL SYSTEM INFORMATION:
- Speed Status: {speed_status}
- Overshoot: {overshoot}
- Oscillation: {oscillation}

DETERMINISTIC ENGINEERING TOOL RESULTS:
- Equipment Health Score: {eng_result['health_score']} / 100
- Engineering Risk Level: {eng_result['risk_level']}
- Temperature Note: {eng_result['temperature']['note']}
- Vibration Note: {eng_result['vibration']['note']}
- Current Note: {eng_result['current']['note']}
""".strip()

    if API_KEY is None:
        st.error(
            "Cannot run AI agent analysis: GROQ_API_KEY is missing. "
            "Configure it in Streamlit secrets and try again.",
            icon="🚫",
        )
    else:
        with st.spinner("Supervisor Agent is analyzing the case and selecting specialist agents..."):
            try:
                result = agent_system.run_complete_analysis(equipment_context)
                st.session_state.analysis_result = result
                st.session_state.equipment_context = equipment_context
            except Exception as exc:  # noqa: BLE001
                st.error(f"Analysis failed unexpectedly: {exc}", icon="🚫")

# ======================================================
# RESULTS DISPLAY
# ======================================================
eng_result = st.session_state.engineering_result
analysis_result = st.session_state.analysis_result

if eng_result:
    st.divider()
    st.subheader("🩺 Equipment Health Dashboard")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Health Score", f"{eng_result['health_score']} / 100")
    with col2:
        risk_color = {
            "LOW": "🟢", "MODERATE": "🟡", "HIGH": "🟠", "CRITICAL": "🔴"
        }.get(eng_result["risk_level"], "⚪")
        st.metric("Risk Level", f"{risk_color} {eng_result['risk_level']}")
    with col3:
        st.metric("Temperature Status", eng_result["temperature"]["status"])
    with col4:
        st.metric("Vibration Status", eng_result["vibration"]["status"])

    gauge_fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=eng_result["health_score"],
            title={"text": "Equipment Health Score"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#6C7BFF"},
                "steps": [
                    {"range": [0, 30], "color": "#3d1f1f"},
                    {"range": [30, 55], "color": "#4d3a1f"},
                    {"range": [55, 80], "color": "#3a4d2a"},
                    {"range": [80, 100], "color": "#1f4d2e"},
                ],
            },
        )
    )
    gauge_fig.update_layout(height=280, margin=dict(t=40, b=10))
    st.plotly_chart(gauge_fig, use_container_width=True)

if analysis_result:
    st.divider()
    st.subheader("🧭 Supervisor Decision")
    st.info(
        "Selected Agents: " + ", ".join(analysis_result["selected_agents"]),
        icon="🧠",
    )

    st.subheader("🤖 Individual Agent Results")
    label_map = {
        "DATA": "📊 Data Analysis Agent",
        "FAULT": "🚨 Fault Diagnosis Agent",
        "CONTROL": "🎛️ Control Engineering Agent",
        "MAINTENANCE": "🛠️ Maintenance Agent",
        "RISK": "⚠️ Risk Assessment Agent",
    }
    tabs = st.tabs([label_map[a] for a in analysis_result["selected_agents"]])
    for tab, agent_name in zip(tabs, analysis_result["selected_agents"]):
        with tab:
            st.markdown(analysis_result["agent_outputs"].get(agent_name, "No output."))

    st.divider()
    st.subheader("📄 Final AI Engineering Report")
    st.markdown(analysis_result["final_report"])

    st.download_button(
        "⬇️ Download Report",
        data=analysis_result["final_report"],
        file_name="mechai_engineering_report.txt",
        mime="text/plain",
        use_container_width=True,
    )

# ======================================================
# ENGINEERING CHAT ASSISTANT
# ======================================================
st.divider()
st.subheader("💬 Ask MechAI Engineering Chat")

for role, message in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(message)

chat_input = st.chat_input("Ask about faults, PID tuning, maintenance, vibration, etc.")
if chat_input:
    st.session_state.chat_history.append(("user", chat_input))
    with st.chat_message("user"):
        st.markdown(chat_input)

    if API_KEY is None:
        reply = "⚠️ Cannot answer: GROQ_API_KEY is not configured."
    else:
        context = st.session_state.get("equipment_context")
        with st.spinner("Thinking..."):
            reply = agent_system.engineering_chat(chat_input, equipment_context=context)

    st.session_state.chat_history.append(("assistant", reply))
    with st.chat_message("assistant"):
        st.markdown(reply)

# ======================================================
# FOOTER
# ======================================================
st.divider()
st.caption(
    "MechAI Copilot — Multi-Agent Agentic AI powered by Groq (openai/gpt-oss-120b). "
    "100% software-based · No hardware required."
)
