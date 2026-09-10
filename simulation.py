"""
simulation.py
--------------
Software-only industrial failure simulation for MechAI Copilot.
Generates synthetic sensor time-series (temperature, vibration, current)
for five scenarios, using pandas and numpy. No hardware is required or
assumed -- this project is 100% software-based.
"""

import numpy as np
import pandas as pd

SIMULATION_MODES = [
    "Normal",
    "Bearing Failure",
    "Overload",
    "Control Instability",
    "Critical Failure",
]


def _time_axis(duration_seconds: int = 60, step_seconds: int = 1) -> np.ndarray:
    return np.arange(0, duration_seconds, step_seconds)


def _noise(n: int, scale: float, seed: int = None) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.normal(0, scale, n)


def simulate_normal(n: int, seed: int = 1) -> pd.DataFrame:
    temp = 45 + _noise(n, 1.5, seed)
    vib = 1.2 + _noise(n, 0.2, seed + 1)
    current = 8.0 + _noise(n, 0.4, seed + 2)
    return temp, vib, current


def simulate_bearing_failure(n: int, seed: int = 2) -> pd.DataFrame:
    t = np.linspace(0, 1, n)
    temp = 45 + 25 * t + _noise(n, 2.0, seed)
    vib = 1.5 + 5.5 * (t ** 1.5) + _noise(n, 0.4, seed + 1)
    current = 8.0 + 2.0 * t + _noise(n, 0.5, seed + 2)
    return temp, vib, current


def simulate_overload(n: int, seed: int = 3) -> pd.DataFrame:
    t = np.linspace(0, 1, n)
    temp = 48 + 30 * t + _noise(n, 2.0, seed)
    vib = 1.8 + 1.5 * t + _noise(n, 0.3, seed + 1)
    current = 9.0 + 14.0 * t + _noise(n, 0.8, seed + 2)
    return temp, vib, current


def simulate_control_instability(n: int, seed: int = 4) -> pd.DataFrame:
    t = np.linspace(0, 8 * np.pi, n)
    temp = 50 + 3 * np.sin(t / 4) + _noise(n, 1.0, seed)
    vib = 2.0 + 1.8 * np.abs(np.sin(t)) + _noise(n, 0.3, seed + 1)
    current = 9.0 + 4.0 * np.abs(np.sin(t * 1.3)) + _noise(n, 0.6, seed + 2)
    return temp, vib, current


def simulate_critical_failure(n: int, seed: int = 5) -> pd.DataFrame:
    t = np.linspace(0, 1, n)
    temp = 55 + 55 * (t ** 1.2) + _noise(n, 2.5, seed)
    vib = 2.5 + 9.0 * (t ** 1.3) + _noise(n, 0.5, seed + 1)
    current = 10.0 + 15.0 * (t ** 1.1) + _noise(n, 1.0, seed + 2)
    return temp, vib, current


_SIMULATORS = {
    "Normal": simulate_normal,
    "Bearing Failure": simulate_bearing_failure,
    "Overload": simulate_overload,
    "Control Instability": simulate_control_instability,
    "Critical Failure": simulate_critical_failure,
}


def run_simulation(mode: str, duration_seconds: int = 60, seed: int = 42) -> pd.DataFrame:
    """
    Generate a synthetic sensor time-series DataFrame for the given
    simulation mode. Columns: Time, Temperature, Vibration, Current.
    """
    if mode not in _SIMULATORS:
        raise ValueError(
            f"Unknown simulation mode '{mode}'. Valid modes: {list(_SIMULATORS.keys())}"
        )

    time_axis = _time_axis(duration_seconds)
    n = len(time_axis)
    temp, vib, current = _SIMULATORS[mode](n, seed=seed)

    df = pd.DataFrame(
        {
            "Time": time_axis,
            "Temperature": np.round(temp, 2),
            "Vibration": np.round(np.clip(vib, 0, None), 2),
            "Current": np.round(np.clip(current, 0, None), 2),
        }
    )
    return df


def get_latest_reading(df: pd.DataFrame) -> dict:
    """
    Convenience helper: pull the final (most recent) row of a simulated
    DataFrame as a plain dict of sensor values for feeding into the
    engineering tools / AI agents.
    """
    last_row = df.iloc[-1]
    return {
        "temperature": float(last_row["Temperature"]),
        "vibration": float(last_row["Vibration"]),
        "current": float(last_row["Current"]),
    }
