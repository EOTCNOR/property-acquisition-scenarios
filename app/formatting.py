from __future__ import annotations

import streamlit as st


def nok(value: float) -> str:
    return f"NOK {value:,.0f}".replace(",", " ")


def millions(value: float) -> float:
    return value / 1_000_000


def fmt_m(value: float) -> str:
    return f"{millions(value):.2f}M"


def weighted_average(pairs: list[tuple[float, float]]) -> float:
    numerator = sum(value * weight for value, weight in pairs)
    denominator = sum(weight for _, weight in pairs)
    return numerator / denominator if denominator else 0.0


def risk_label(score: float) -> str:
    if score < 35:
        return "Manageable"
    if score < 55:
        return "Elevated"
    if score < 75:
        return "High"
    return "Severe"


def signed_nok(value: float) -> str:
    if value > 0:
        return f"+{nok(value)}"
    if value < 0:
        return f"-{nok(abs(value))}"
    return nok(0)


def signed_m(value: float) -> str:
    if value > 0:
        return f"+{fmt_m(value)}"
    if value < 0:
        return f"-{fmt_m(abs(value))}"
    return "0.00M"


def clamp_index(value: int, length: int) -> int:
    if length <= 0:
        return 0
    return max(0, min(value, length - 1))


def sidebar_summary_row(label: str, value: str, note: str | None = None, note_color: str = "#6b7280") -> None:
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:baseline; gap:0.75rem; margin:0.2rem 0;">
            <span style="font-size:0.96rem;">{label}</span>
            <span style="font-size:0.96rem; font-weight:600; white-space:nowrap;">{value}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if note:
        st.markdown(
            f"""
            <div style="font-size:0.88rem; color:{note_color}; margin:0 0 0.55rem 0;">{note}</div>
            """,
            unsafe_allow_html=True,
        )

