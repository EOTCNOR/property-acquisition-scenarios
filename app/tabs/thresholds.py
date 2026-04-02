from __future__ import annotations

import streamlit as st

from app.formatting import nok, signed_nok


def render_thresholds_tab(tab, ctx: dict) -> None:
    with tab:
        st.subheader("Affordability thresholds")
        st.caption(
            f"This tab answers one practical question: how much recurring annual cash flow is needed to carry `{ctx['candidate_building_name']}` alone, both buildings during overlap, and the bridge period before sale."
        )
        member_gap_one = ctx["annual_member_cashflow"] - ctx["one_building_threshold"]
        member_gap_both = ctx["annual_member_cashflow"] - ctx["both_buildings_threshold"]
        bridge_total_need = max(ctx["funding_gap"], 0.0) + ctx["renovation_spend_before_sale"] + ctx["overlap_cost"] + ctx["debt_service_during_overlap"]
        t1, t2, t3 = st.columns(3)
        t1.metric("Annual free cash after church operations", nok(ctx["annual_member_cashflow"]), help="Annual free cash left after normal church staff and operating costs are already covered. This is the amount available to support the property strategy.")
        t2.metric(f"Needed to carry {ctx['candidate_building_name']}", nok(ctx["one_building_threshold"]), signed_nok(member_gap_one), help="How much recurring annual cash flow is needed to carry the candidate building alone after property income.")
        t3.metric("Needed to carry both buildings", nok(ctx["both_buildings_threshold"]), signed_nok(member_gap_both), help="How much recurring annual cash flow is needed if both the candidate and current buildings must be carried at the same time after property income.")
        bt1, bt2 = st.columns(2)
        bt1.metric("Total cash needed before sale", nok(bridge_total_need), help="One-time cash needed before the current building is sold, including purchase gap, selected renovation cost, overlap cost, and loan payments before sale.")
        bt2.metric("Recurring gap if both buildings kept", nok(max(ctx["both_buildings_threshold"] - ctx["annual_member_cashflow"], 0.0)), help="How much recurring annual cash flow is still missing if both buildings must be carried at the same time.")
        st.caption("Recurring annual cash flow is different from the one-time cash needed before sale. The bridge figure includes purchase gap, selected renovation cost, overlap cost, and loan payments before sale.")

