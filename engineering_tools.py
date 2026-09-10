"""
engineering_tools.py
---------------------
Deterministic, rule-based engineering calculations for MechAI Copilot.

IMPORTANT: These functions are NOT AI-based. They implement fixed
engineering thresholds and formulas so that health scoring and risk
calculation are consistent, explainable, and reproducible. The AI agents
receive the output of these tools as grounding context -- the AI does not
replace these calculations.

Workflow:
SENSOR DATA -> ENGINEERING TOOLS -> HEALTH SCORE -> RISK CALCULATION -> AI AGENTS
"""

from typing import Dict, Any


# ==================================================
# THRESHOLDS (adjust here to re-tune the whole system)
# ==================================================
TEMP_NORMAL_MAX = 70.0      # deg C
TEMP_WARNING_MAX = 90.0     # deg C

VIBRATION_NORMAL_MAX = 2.8   # mm/s
VIBRATION_WARNING_MAX = 4.5  # mm/s

CURRENT_NORMAL_MAX = 15.0    # A (example nominal rating)
CURRENT_WARNING_MAX = 20.0   # A


def analyze_temperature(temperature: float) -> Dict[str, Any]:
    """
    Classify a temperature reading (deg C) into a status band and
    return a short deterministic explanation.
    """
    try:
        temperature = float(temperature)
    except (TypeError, ValueError):
        return {"value": None, "status": "UNKNOWN", "note": "Invalid temperature value."}

    if temperature <= TEMP_NORMAL_MAX:
        status = "NORMAL"
        note = "Temperature within normal operating range."
    elif temperature <= TEMP_WARNING_MAX:
        status = "WARNING"
        note = "Temperature elevated above normal range; monitor closely."
    else:
        status = "CRITICAL"
        note = "Temperature critically high; risk of thermal damage."

    return {"value": temperature, "status": status, "note": note}


def analyze_vibration(vibration: float) -> Dict[str, Any]:
    """
    Classify a vibration reading (mm/s RMS) into a status band.
    """
    try:
        vibration = float(vibration)
    except (TypeError, ValueError):
        return {"value": None, "status": "UNKNOWN", "note": "Invalid vibration value."}

    if vibration <= VIBRATION_NORMAL_MAX:
        status = "NORMAL"
        note = "Vibration levels within acceptable ISO range."
    elif vibration <= VIBRATION_WARNING_MAX:
        status = "WARNING"
        note = "Vibration elevated; possible imbalance, misalignment, or early bearing wear."
    else:
        status = "CRITICAL"
        note = "Vibration critically high; strong indication of mechanical fault."

    return {"value": vibration, "status": status, "note": note}


def analyze_current(current: float) -> Dict[str, Any]:
    """
    Classify a motor current reading (A) into a status band.
    """
    try:
        current = float(current)
    except (TypeError, ValueError):
        return {"value": None, "status": "UNKNOWN", "note": "Invalid current value."}

    if current <= CURRENT_NORMAL_MAX:
        status = "NORMAL"
        note = "Motor current within normal load range."
    elif current <= CURRENT_WARNING_MAX:
        status = "WARNING"
        note = "Motor current elevated; possible overload or mechanical drag."
    else:
        status = "CRITICAL"
        note = "Motor current critically high; risk of winding damage / overload trip."

    return {"value": current, "status": status, "note": note}


def calculate_health_score(
    temperature: float,
    vibration: float,
    current: float,
    speed_status: str = "Stable",
    overshoot: str = "Normal",
    oscillation: str = "No",
) -> int:
    """
    Compute a deterministic 0-100 equipment health score from sensor and
    control-loop inputs. 100 = perfectly healthy, 0 = critical.
    """
    score = 100

    temp_result = analyze_temperature(temperature)
    vib_result = analyze_vibration(vibration)
    cur_result = analyze_current(current)

    for result, warn_penalty, crit_penalty in (
        (temp_result, 15, 30),
        (vib_result, 15, 30),
        (cur_result, 15, 30),
    ):
        if result["status"] == "WARNING":
            score -= warn_penalty
        elif result["status"] == "CRITICAL":
            score -= crit_penalty

    if str(speed_status).strip().lower() == "unstable":
        score -= 10

    overshoot_norm = str(overshoot).strip().lower()
    if overshoot_norm == "high":
        score -= 10
    elif overshoot_norm == "low":
        score -= 3

    if str(oscillation).strip().lower() == "yes":
        score -= 10

    return max(0, min(100, score))


def calculate_risk(health_score: int) -> str:
    """
    Map a health score to a discrete engineering risk level.
    """
    if health_score >= 80:
        return "LOW"
    elif health_score >= 55:
        return "MODERATE"
    elif health_score >= 30:
        return "HIGH"
    else:
        return "CRITICAL"


def run_engineering_analysis(
    temperature: float,
    vibration: float,
    current: float,
    speed_status: str = "Stable",
    overshoot: str = "Normal",
    oscillation: str = "No",
) -> Dict[str, Any]:
    """
    Run the full deterministic engineering analysis pipeline and return a
    structured dictionary that is passed to the AI agents as grounding
    context. This is the single entry point app.py / agent_system.py
    should call.
    """
    temp_result = analyze_temperature(temperature)
    vib_result = analyze_vibration(vibration)
    cur_result = analyze_current(current)

    health_score = calculate_health_score(
        temperature=temperature,
        vibration=vibration,
        current=current,
        speed_status=speed_status,
        overshoot=overshoot,
        oscillation=oscillation,
    )
    risk_level = calculate_risk(health_score)

    return {
        "temperature": temp_result,
        "vibration": vib_result,
        "current": cur_result,
        "speed_status": speed_status,
        "overshoot": overshoot,
        "oscillation": oscillation,
        "health_score": health_score,
        "risk_level": risk_level,
    }
