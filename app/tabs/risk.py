from __future__ import annotations

import streamlit as st

from app.formatting import nok, risk_label, weighted_average


def render_risk_tab(tab, ctx: dict, default, description) -> None:
    with tab:
        st.subheader("Scenario-level risk")
        col1, col2 = st.columns(2)

        with col1:
            lease_lock_in = st.slider("Lease lock-in pressure", 0, 100, default("risk", "lease_lock_in", 70), help=description("risk", "lease_lock_in", "How much current leases restrict your timing and flexibility. Higher values mean less freedom to repurpose space quickly."))
            conversion_uncertainty = st.slider("Conversion / structural uncertainty", 0, 100, default("risk", "conversion_uncertainty", 65), help=description("risk", "conversion_uncertainty", "How uncertain you are about layout changes, structure, and hidden building work. Higher values raise overall project risk."))
            approvals_risk = st.slider("Fire, egress, ventilation, approvals risk", 0, 100, default("risk", "approvals_risk", 70), help=description("risk", "approvals_risk", "How difficult technical approval and compliance may be around fire, egress, ventilation, and related building requirements. Higher values increase expected delay and cost risk."))
            regulation_risk = st.slider("Regulation / use-permission risk", 0, 100, default("risk", "regulation_risk", 70), help=description("risk", "regulation_risk", "How uncertain lawful use, zoning, assembly permission, or other regulatory permission may be. Higher values mean more risk that the intended church use is delayed, restricted, or blocked."))
            financing_pressure = st.slider("Financing pressure", 0, 100, default("risk", "financing_pressure", 75), help=description("risk", "financing_pressure", "How tight the financing picture feels. Higher values mean less room for surprises in purchase price, timing, or cost escalation."))

        with col2:
            income_dependency = st.slider("Dependence on rental income", 0, 100, default("risk", "income_dependency", 60), help=description("risk", "income_dependency", "How much the project depends on rent or shared-use income. Higher values mean the case weakens more if tenants or events underperform."))
            market_buffer = st.slider("Market/value cushion", 0, 100, default("risk", "market_buffer", 40), help=description("risk", "market_buffer", "How much price cushion you believe exists. Higher values improve resilience because the purchase feels less stretched."))
            management_complexity = st.slider("Management / transition complexity", 0, 100, default("risk", "management_complexity", 55), help=description("risk", "management_complexity", "How hard the transition will be to manage operationally. Higher values mean more execution risk and more chance of friction or delay."))
            contingency_cover = st.slider("Contingency strength", 0, 100, default("risk", "contingency_cover", 45), help=description("risk", "contingency_cover", "How strong your fallback reserves and mitigations are. Higher values reduce effective project risk."))

        gap_ratio = max(ctx["funding_gap"], 0) / ctx["acquisition_cost"] if ctx["acquisition_cost"] else 0.0
        leverage_ratio = ctx["loan_used"] / ctx["acquisition_cost"] if ctx["acquisition_cost"] else 0.0
        financing_score = min(100.0, financing_pressure * 0.6 + gap_ratio * 200 + leverage_ratio * 25)
        resilience_penalty = 100 - contingency_cover
        cushion_penalty = 100 - market_buffer
        overall_risk = weighted_average(
            [
                (lease_lock_in, 0.16),
                (conversion_uncertainty, 0.15),
                (approvals_risk, 0.12),
                (regulation_risk, 0.12),
                (financing_score, 0.20),
                (income_dependency, 0.10),
                (management_complexity, 0.08),
                (resilience_penalty, 0.05),
                (cushion_penalty, 0.02),
            ]
        )

        st.metric("Overall risk score", f"{overall_risk:.0f} / 100", risk_label(overall_risk))
        st.progress(min(max(overall_risk / 100, 0.0), 1.0))

        drivers = [
            ("Lease lock-in", lease_lock_in),
            ("Conversion uncertainty", conversion_uncertainty),
            ("Approvals and compliance", approvals_risk),
            ("Regulation / use-permission", regulation_risk),
            ("Financing", financing_score),
            ("Income dependency", income_dependency),
            ("Transition complexity", management_complexity),
        ]
        drivers.sort(key=lambda item: item[1], reverse=True)
        st.markdown("Top current risk drivers:")
        for name, score in drivers[:3]:
            st.write(f"- {name}: {score:.0f}/100")

        if ctx["funding_gap"] > 0:
            st.error(f"Current funding gap at this bid: {nok(ctx['funding_gap'])}")
        else:
            st.success(f"Cash left after acquisition: {nok(max(ctx['cash_left_after_acquisition'], 0.0))}")

