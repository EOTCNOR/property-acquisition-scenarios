from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from app.formatting import nok
from app.member_distribution import (
    CURRENT_CHURCH_COORDINATES,
    CURRENT_CHURCH_LABEL,
    build_member_point_distribution,
    load_member_distribution,
    summarize_location,
)


def _decision_reading(ctx: dict, candidate_member_fit: dict[str, float | str]) -> list[str]:
    notes: list[str] = []
    proceed_signal = str(ctx.get("screening_proceed_signal", "Proceed With Conditions"))
    if proceed_signal == "Proceed":
        notes.append("Overall position: this case currently looks strong enough to justify deeper acquisition work.")
    elif proceed_signal == "Proceed With Conditions":
        notes.append("Overall position: this case is plausible, but it still depends on clearing the unresolved blockers cleanly.")
    else:
        notes.append("Overall position: this case still looks too fragile for a confident acquisition push.")

    candidate_within_10 = float(candidate_member_fit["share_within_10km_pct"])
    current_within_10 = float(ctx.get("summary_current_within_10km_pct", 0.0))
    candidate_weighted = float(candidate_member_fit["weighted_avg_distance_km"])
    current_weighted = float(ctx.get("summary_current_weighted_distance_km", 0.0))
    if candidate_weighted <= current_weighted and candidate_within_10 >= current_within_10:
        notes.append("Member fairness: this candidate is at least as fair as the current church on whole-network distance and also improves practical reach.")
    elif candidate_within_10 > current_within_10:
        notes.append("Member fairness: this candidate improves near-member reach, but some of that gain comes with a wider whole-network distance tradeoff.")
    else:
        notes.append("Member fairness: this candidate does not currently improve the whole-member geography enough to be considered an obvious upgrade.")

    bridge_shortfall = float(ctx.get("bridge_shortfall", 0.0))
    income_coverage = float(ctx.get("income_coverage", 0.0))
    if bridge_shortfall <= 0 and income_coverage >= 1.0:
        notes.append("Financial pressure: the current case is carryable on both transition cash and recurring property support.")
    elif bridge_shortfall > 0:
        notes.append("Financial pressure: the bridge period before sale is still the main cash pressure point and needs a funding answer.")
    else:
        notes.append("Financial pressure: transition cash looks manageable, but recurring income support is still tight against annual debt service.")

    return notes


def render_executive_summary_tab(tab, ctx: dict, label) -> None:
    with tab:
        st.subheader(label("summary.title", "Executive summary"))
        st.caption(
            label("summary.caption", "This page is for board and elder review. It pulls the main conclusion from the detailed tabs into one decision view.")
        )

        df = load_member_distribution(str(Path(__file__).resolve().parents[2]))
        member_points = build_member_point_distribution(df)
        current_church = summarize_location(
            member_points,
            CURRENT_CHURCH_COORDINATES[0],
            CURRENT_CHURCH_COORDINATES[1],
            CURRENT_CHURCH_LABEL,
        )
        candidate_label = ctx.get("candidate_building_address") or ctx.get("candidate_building_name") or "Candidate property"
        candidate_summary = summarize_location(
            member_points,
            float(ctx["candidate_building_latitude"]),
            float(ctx["candidate_building_longitude"]),
            str(candidate_label),
        )
        ctx["summary_current_weighted_distance_km"] = float(current_church["weighted_avg_distance_km"])
        ctx["summary_current_within_10km_pct"] = float(current_church["share_within_10km_pct"])

        k1, k2, k3, k4 = st.columns(4)
        k1.metric(label("summary.metrics.proceed_signal", "Proceed signal"), str(ctx.get("screening_proceed_signal", "n/a")))
        k2.metric(label("summary.metrics.gateway_score", "Gateway score"), f"{float(ctx.get('screening_score', 0.0)):.0f}/100")
        k3.metric(label("summary.metrics.core_checks_confirmed", "Core checks confirmed"), f"{int(ctx.get('screening_confirmed_core_checks', 0))}/4")
        k4.metric(label("summary.metrics.largest_unresolved_area", "Largest unresolved area"), str(ctx.get("screening_largest_unresolved_area", "n/a")))

        st.markdown(f"### {label('summary.sections.recommendation', 'Recommendation Snapshot')}")
        for note in _decision_reading(ctx, candidate_summary):
            st.write(f"- {note}")

        st.markdown(f"### {label('summary.sections.pillars', 'Decision Pillars')}")
        pillars = pd.DataFrame(
            [
                {
                    "Pillar": "Gateway and diligence",
                    "Current reading": str(ctx.get("screening_proceed_signal", "n/a")),
                    "Key number": f"{float(ctx.get('screening_score', 0.0)):.0f}/100",
                    "Why it matters": "Shows whether the case is strong enough to deserve time, money, and leadership attention now.",
                },
                {
                    "Pillar": "Member geography",
                    "Current reading": f"{candidate_summary['weighted_avg_distance_km']:.1f} km weighted avg",
                    "Key number": f"{candidate_summary['share_within_10km_pct']:.1f}% within 10 km",
                    "Why it matters": "Tests fairness across the whole membership, not just one favored corridor.",
                },
                {
                    "Pillar": "Floor program",
                    "Current reading": f"{int(ctx.get('space_assembly_floor', 1))} assembly floor, {int(ctx.get('space_total_support_rooms', 0))} support rooms",
                    "Key number": f"{int(ctx.get('space_likely_capacity', 0))} likely seats",
                    "Why it matters": "Shows whether the building can actually carry worship, classrooms, offices, and weekday ministry.",
                },
                {
                    "Pillar": "Renovation burden",
                    "Current reading": nok(float(ctx.get("selected_renovation_total", 0.0))),
                    "Key number": nok(float(ctx.get("renovation_funding_needed", 0.0))),
                    "Why it matters": "Separates purchase affordability from the real cost of making the building usable.",
                },
                {
                    "Pillar": "Income support",
                    "Current reading": nok(float(ctx.get("total_expected_net_income", 0.0))),
                    "Key number": f"{float(ctx.get('income_coverage', 0.0)):.2f}x debt coverage",
                    "Why it matters": "Shows how much of the yearly carrying cost is supported by realistic property income.",
                },
                {
                    "Pillar": "Bridge / transition",
                    "Current reading": nok(float(ctx.get("bridge_shortfall", 0.0))),
                    "Key number": f"{int(ctx.get('overlap_months', 0))} overlap months",
                    "Why it matters": "This is often where otherwise reasonable deals fail in practice.",
                },
            ]
        )
        st.dataframe(pillars, use_container_width=True, hide_index=True)

        st.markdown(f"### {label('summary.sections.compare_current', 'Candidate Compared With Current Church')}")
        compare_df = pd.DataFrame(
            [
                {
                    "Location": str(candidate_summary["label"]),
                    "Weighted avg distance (km)": round(float(candidate_summary["weighted_avg_distance_km"]), 1),
                    "Within 5 km (%)": round(float(candidate_summary["share_within_5km_pct"]), 1),
                    "Within 10 km (%)": round(float(candidate_summary["share_within_10km_pct"]), 1),
                    "Within 20 km (%)": round(float(candidate_summary["share_within_20km_pct"]), 1),
                },
                {
                    "Location": CURRENT_CHURCH_LABEL,
                    "Weighted avg distance (km)": round(float(current_church["weighted_avg_distance_km"]), 1),
                    "Within 5 km (%)": round(float(current_church["share_within_5km_pct"]), 1),
                    "Within 10 km (%)": round(float(current_church["share_within_10km_pct"]), 1),
                    "Within 20 km (%)": round(float(current_church["share_within_20km_pct"]), 1),
                },
            ]
        )
        st.dataframe(compare_df, use_container_width=True, hide_index=True)
        st.caption(
            label("summary.compare_caption", "Use this section to answer a practical board question: if we move to this exact property, do we improve member access fairly compared with where we are today?")
        )

        st.markdown(f"### {label('summary.sections.bottom_line', 'Current Bottom Line')}")
        b1, b2, b3, b4 = st.columns(4)
        b1.metric(label("summary.metrics.selected_renovation_cost", "Selected renovation cost"), nok(float(ctx.get("selected_renovation_total", 0.0))))
        b2.metric(label("summary.metrics.net_property_income", "Net property income"), nok(float(ctx.get("total_expected_net_income", 0.0))))
        b3.metric(label("summary.metrics.bridge_shortfall", "Bridge shortfall"), nok(float(ctx.get("bridge_shortfall", 0.0))))
        b4.metric(label("summary.metrics.financial_risk_score", "Financial risk score"), f"{float(ctx.get('screening_financial_risk', 0.0)):.0f}/100")
        st.caption(
            label("summary.bottom_line_caption", "This page reuses the live outputs from the detailed tabs so the board summary stays consistent with the working case.")
        )
