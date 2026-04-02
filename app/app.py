from __future__ import annotations

from pathlib import Path

import streamlit as st

from app.config import AppConfig
from app.tabs import (
    render_executive_summary_tab,
    render_hall_tab,
    render_income_tab,
    render_member_geography_tab,
    render_mortgage_tab,
    render_operations_tab,
    render_renovation_tab,
    render_scenario_paths_tab,
    render_screening_tab,
    render_sidebar,
    render_thresholds_tab,
)

APP_CONFIG = AppConfig(Path(__file__).resolve().parents[1])


def default(section: str, key: str, fallback):
    return APP_CONFIG.default(section, key, fallback)


def description(section: str, key: str, fallback: str) -> str:
    return APP_CONFIG.description(section, key, fallback)


def label(path: str, fallback: str) -> str:
    return APP_CONFIG.label(path, fallback)


def run() -> None:
    st.set_page_config(
        page_title=label("app.page_title", "Property Acquisition Scenarios Tool"),
        page_icon="🏢",
        layout="wide",
    )

    st.markdown(
        """
        <style>
        html, body, [class*="css"] {
            font-size: 17px;
        }
        p, li, label, div[data-testid="stMarkdownContainer"] {
            font-size: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title(label("app.title", "Property Acquisition Scenarios Tool"))
    st.caption(
        label(
            "app.caption",
            "Planning support only. Use this to compare acquisition and transition scenarios, not to produce legal, valuation, or construction-grade numbers.",
        )
    )

    ctx = render_sidebar(default, description, label)

    summary_tab, screening_tab, member_geo_tab, renovation_tab, income_tab, hall_tab, mortgage_tab, ops_tab, exit_path_tab, threshold_tab = st.tabs(
        [
            label("tabs.summary", "Executive Summary"),
            label("tabs.screening", "Screening Framework"),
            label("tabs.member_geography", "Member Geography"),
            label("tabs.renovation", "Renovation Cost"),
            label("tabs.income", "Income Generation"),
            label("tabs.space", "Space Utilization"),
            label("tabs.mortgage", "Mortgage Plan"),
            label("tabs.overlap", "Portfolio Overlap"),
            label("tabs.scenarios", "Scenario Paths"),
            label("tabs.thresholds", "Thresholds"),
        ]
    )

    render_screening_tab(screening_tab, ctx, default, label)
    render_member_geography_tab(member_geo_tab, ctx)
    render_renovation_tab(renovation_tab, ctx, default, description, label)
    render_income_tab(income_tab, ctx, default, description, label)
    render_hall_tab(hall_tab, ctx, default, label)
    render_mortgage_tab(mortgage_tab, ctx, default, description)
    render_operations_tab(ops_tab, ctx, default, description)
    render_scenario_paths_tab(exit_path_tab, ctx, default, description)
    render_thresholds_tab(threshold_tab, ctx)
    render_executive_summary_tab(summary_tab, ctx, label)
