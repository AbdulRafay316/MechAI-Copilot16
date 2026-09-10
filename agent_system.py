"""
agent_system.py
-----------------
MechAI Copilot multi-agent orchestration system.

This module previously used Google Gemini (google-genai). It has been
COMPLETELY migrated to the Groq API using the official Groq Python SDK.
No Gemini code, imports, or environment variables remain.

Model in use: openai/gpt-oss-120b (served via Groq)

Agents:
1. Supervisor Agent        -> select_agents()
2. Data Analysis Agent      -> data_agent()
3. Fault Diagnosis Agent    -> fault_agent()
4. Control Engineering Agent -> control_agent()
5. Maintenance Agent        -> maintenance_agent()
6. Risk Assessment Agent    -> risk_agent()
7. Final Report Agent       -> report_agent()
8. Engineering Chat Assistant -> engineering_chat()

Workflow:
USER INPUT -> SUPERVISOR AGENT -> AGENT SELECTION ->
[DATA / FAULT / CONTROL / MAINTENANCE / RISK agents] ->
FINAL REPORT AGENT -> ENGINEERING REPORT
"""

import re
from typing import Dict, List, Optional, Any

from groq import Groq

from prompts import (
    SUPERVISOR_PROMPT,
    DATA_AGENT_PROMPT,
    FAULT_AGENT_PROMPT,
    CONTROL_AGENT_PROMPT,
    MAINTENANCE_AGENT_PROMPT,
    RISK_AGENT_PROMPT,
    FINAL_REPORT_PROMPT,
    CHAT_ASSISTANT_PROMPT,
)

VALID_AGENTS = ["DATA", "FAULT", "CONTROL", "MAINTENANCE", "RISK"]
FALLBACK_AGENTS = ["DATA", "FAULT", "MAINTENANCE", "RISK"]


class MechAIAgentSystem:
    """
    Core orchestration class for the MechAI Copilot agentic AI system.
    Wraps the Groq API and coordinates the specialist engineering agents.
    """

    def __init__(self, api_key: Optional[str], model: str = "openai/gpt-oss-120b"):
        """
        Initialize the Groq client.

        Note: api_key may be None (e.g. missing Streamlit secret). In that
        case the client is not created, and ask_agent() will return a
        clear, user-friendly error instead of crashing.
        """
        self.model = model
        self.api_key = api_key
        self.client = None

        if api_key:
            try:
                self.client = Groq(api_key=api_key)
            except Exception as exc:  # noqa: BLE001
                self.client = None
                self.init_error = f"Failed to initialize Groq client: {exc}"
        else:
            self.init_error = "Groq API key is missing."

    # ==================================================
    # CORE AI REQUEST FUNCTION
    # ==================================================
    def ask_agent(self, system_prompt: str, user_data: str) -> str:
        """
        Generic function used by every agent to talk to the Groq API.

        1. Accepts a system prompt (agent specialization).
        2. Accepts user_data (equipment context / question).
        3. Sends the request to Groq using self.model.
        4. Returns only the AI response text.
        5. Handles all failure modes with meaningful error messages.
        """
        if self.client is None:
            return (
                "⚠️ AI request failed: Groq API key is missing or invalid. "
                "Please configure GROQ_API_KEY in Streamlit secrets."
            )

        if not user_data or not str(user_data).strip():
            return "⚠️ AI request skipped: no equipment data was provided."

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": str(user_data)},
                ],
                temperature=0.3,
                max_tokens=1500,
            )

            if not response or not getattr(response, "choices", None):
                return "⚠️ AI request failed: empty response received from Groq."

            content = response.choices[0].message.content
            if not content or not content.strip():
                return "⚠️ AI request failed: the model returned an empty response."

            return content.strip()

        except Exception as exc:  # noqa: BLE001
            return self._handle_api_error(exc)

    @staticmethod
    def _handle_api_error(exc: Exception) -> str:
        """
        Translate low-level Groq/HTTP exceptions into clear,
        user-friendly, non-sensitive error messages.
        """
        message = str(exc).lower()

        if "401" in message or "invalid api key" in message or "unauthorized" in message:
            return "⚠️ AI request failed: the Groq API key is invalid. Please check GROQ_API_KEY."
        if "429" in message or "rate limit" in message:
            return "⚠️ AI request failed: Groq API rate limit reached. Please wait and try again."
        if "model" in message and ("not found" in message or "does not exist" in message):
            return "⚠️ AI request failed: the requested model is unavailable. Please verify the model name."
        if "timeout" in message or "timed out" in message:
            return "⚠️ AI request failed: the request to Groq timed out. Please check your network connection."
        if "connection" in message or "network" in message or "dns" in message:
            return "⚠️ AI request failed: network error while contacting Groq. Please check your internet connection."

        return "⚠️ AI request failed due to an unexpected error. Please try again."

    # ==================================================
    # SUPERVISOR AGENT
    # ==================================================
    def select_agents(self, equipment_context: str) -> List[str]:
        """
        Ask the Supervisor Agent which specialist agents should run, then
        clean, validate, and return the agent list. Falls back to a safe
        default set if the Supervisor response is unusable.
        """
        raw_response = self.ask_agent(SUPERVISOR_PROMPT, equipment_context)

        if raw_response.startswith("⚠️"):
            return FALLBACK_AGENTS

        cleaned = raw_response.upper()
        cleaned = cleaned.replace("\n", ",").replace("\r", ",")
        # Extract only known agent tokens using regex to strip any stray
        # formatting, punctuation, or explanatory text the model may add.
        found = re.findall(r"DATA|FAULT|CONTROL|MAINTENANCE|RISK", cleaned)

        # Deduplicate while preserving order
        selected = []
        for agent in found:
            if agent in VALID_AGENTS and agent not in selected:
                selected.append(agent)

        if not selected:
            return FALLBACK_AGENTS

        return selected

    # ==================================================
    # SPECIALIST AGENTS
    # ==================================================
    def data_agent(self, equipment_context: str) -> str:
        """Data Analysis Agent."""
        return self.ask_agent(DATA_AGENT_PROMPT, equipment_context)

    def fault_agent(self, equipment_context: str) -> str:
        """Fault Diagnosis Agent."""
        return self.ask_agent(FAULT_AGENT_PROMPT, equipment_context)

    def control_agent(self, equipment_context: str) -> str:
        """Control Engineering Agent."""
        return self.ask_agent(CONTROL_AGENT_PROMPT, equipment_context)

    def maintenance_agent(self, equipment_context: str) -> str:
        """Maintenance Agent."""
        return self.ask_agent(MAINTENANCE_AGENT_PROMPT, equipment_context)

    def risk_agent(self, equipment_context: str) -> str:
        """Risk Assessment Agent."""
        return self.ask_agent(RISK_AGENT_PROMPT, equipment_context)

    # ==================================================
    # FINAL REPORT AGENT
    # ==================================================
    def report_agent(self, agent_outputs: Dict[str, str], equipment_context: str) -> str:
        """
        Synthesize all specialist agent outputs into one final engineering
        report.
        """
        sections = []
        label_map = {
            "DATA": "DATA ANALYSIS AGENT OUTPUT",
            "FAULT": "FAULT DIAGNOSIS AGENT OUTPUT",
            "CONTROL": "CONTROL ENGINEERING AGENT OUTPUT",
            "MAINTENANCE": "MAINTENANCE AGENT OUTPUT",
            "RISK": "RISK ASSESSMENT AGENT OUTPUT",
        }
        for key, label in label_map.items():
            if key in agent_outputs and agent_outputs[key]:
                sections.append(f"--- {label} ---\n{agent_outputs[key]}")

        combined_input = (
            f"EQUIPMENT CONTEXT:\n{equipment_context}\n\n"
            + "\n\n".join(sections)
        )

        return self.ask_agent(FINAL_REPORT_PROMPT, combined_input)

    # ==================================================
    # FULL PIPELINE
    # ==================================================
    def run_complete_analysis(self, equipment_context: str) -> Dict[str, Any]:
        """
        Run the full agentic pipeline:
        SUPERVISOR -> SELECTED SPECIALIST AGENTS -> FINAL REPORT

        Returns a dictionary containing the selected agents, each agent's
        raw output, and the final synthesized report.
        """
        selected_agents = self.select_agents(equipment_context)

        agent_dispatch = {
            "DATA": self.data_agent,
            "FAULT": self.fault_agent,
            "CONTROL": self.control_agent,
            "MAINTENANCE": self.maintenance_agent,
            "RISK": self.risk_agent,
        }

        agent_outputs: Dict[str, str] = {}
        for agent_name in selected_agents:
            agent_fn = agent_dispatch.get(agent_name)
            if agent_fn is None:
                continue
            try:
                agent_outputs[agent_name] = agent_fn(equipment_context)
            except Exception as exc:  # noqa: BLE001
                agent_outputs[agent_name] = f"⚠️ {agent_name} agent failed: {exc}"

        try:
            final_report = self.report_agent(agent_outputs, equipment_context)
        except Exception as exc:  # noqa: BLE001
            final_report = f"⚠️ Final report generation failed: {exc}"

        return {
            "selected_agents": selected_agents,
            "agent_outputs": agent_outputs,
            "final_report": final_report,
        }

    # ==================================================
    # ENGINEERING CHAT ASSISTANT
    # ==================================================
    def engineering_chat(self, question: str, equipment_context: Optional[str] = None) -> str:
        """
        General-purpose engineering Q&A assistant, specialized in
        mechatronics, control engineering, automation, PLCs, PID control,
        motors, sensors, industrial maintenance, and fault diagnosis.
        """
        if equipment_context:
            user_data = (
                f"CURRENT EQUIPMENT CONTEXT:\n{equipment_context}\n\n"
                f"QUESTION:\n{question}"
            )
        else:
            user_data = f"QUESTION (no equipment context available):\n{question}"

        return self.ask_agent(CHAT_ASSISTANT_PROMPT, user_data)
