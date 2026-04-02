from __future__ import annotations

import streamlit as st

from app.formatting import nok


def render_income_tab(tab, ctx: dict, default, description) -> None:
    with tab:
        st.subheader("Income generation")
        st.caption(
            f"Linked from sidebar financing: actual bank loan used `{nok(ctx['loan_used'])}`, rate `{ctx['nominal_rate']:.2f}%`, term `{ctx['amort_years']}` years."
        )
        assembly_floor_for_income = int(st.session_state.get("space_assembly_floor", 1))
        space_planner_rental_income = 0.0
        for floor_no in range(1, ctx["candidate_floors"] + 1):
            if floor_no == assembly_floor_for_income:
                continue
            floor_use = st.session_state.get(f"space_floor_use_{floor_no}", "Support rooms")
            if floor_use in {"Rental", "Mixed / other"}:
                space_planner_rental_income += float(st.session_state.get(f"space_floor_rental_income_{floor_no}", 0.0))

        income_sources = ["Whole building", "Second floor only"]
        income_source = st.selectbox(
            "Income source assumption",
            income_sources,
            index=default("income", "income_source_index", 0),
            help=description("income", "income_source_index", "Choose whether income scenarios use the whole building or a second-floor-only case after giving the first floor to church use."),
        )

        whole_building_mode = income_source == "Whole building"
        contracted_rent_default = default("income", "contracted_rent", 1_320_078) if whole_building_mode else default("income", "second_floor_contracted_rent", 758_705)
        fallback_additional_income_default = (
            int(
                default("income", "vacant_upside", 711_589) * 0.4
                + default("income", "hall_rental_income", 350_000)
                + default("income", "classroom_office_income", 250_000)
                + default("income", "parking_income", 60_000)
            )
            if whole_building_mode
            else int(
                default("income", "second_floor_vacant_upside", 34_087)
                + default("income", "classroom_office_income", 250_000)
                + default("income", "parking_income", 60_000)
            )
        )
        additional_income_default = int(space_planner_rental_income) if space_planner_rental_income > 0 else fallback_additional_income_default

        col1, col2 = st.columns(2)

        with col1:
            contracted_rent = st.number_input(
                "Existing annual contracted income",
                min_value=0,
                value=contracted_rent_default,
                step=50_000,
                help=(
                    description("income", "contracted_rent", "Current annual rent already contracted. Increasing it improves transition cash support and debt coverage.")
                    if whole_building_mode
                    else description("income", "second_floor_contracted_rent", "Current annual contracted rent visible on the second floor only, based on the prospect's listed rents for the medical center, Makeupediaa, and the psychologist.")
                ),
            )
            retained_lease_income_pct = st.slider("Income likely to continue %", 0.0, 100.0, default("income", "retained_lease_income_pct", 70.0), 1.0, help=description("income", "retained_lease_income_pct", "How much of current lease income survives the transition. Lower values weaken cash support during changeover."))
            expected_collection_pct = st.slider("Cash actually collected %", 0.0, 100.0, default("income", "expected_collection_pct", 95.0), 1.0, help=description("income", "expected_collection_pct", "Expected cash collection quality. Lower values mean income on paper turns into less money in hand."))

        with col2:
            additional_income = st.number_input(
                "Additional realistic annual income",
                min_value=0,
                value=additional_income_default,
                step=25_000,
                help="Expected additional annual income beyond existing contracts, such as rental floors from the floor planner, room use, hall use, parking, or other practical upside you believe is realistic.",
            )
            operating_cost_ratio = st.slider("Running-cost share %", 0.0, 80.0, default("income", "operating_cost_ratio", 28.0), 1.0, help=description("income", "operating_cost_ratio", "Share of gross income lost to operating costs. Increasing it reduces the net amount available for debt and project support."))

        if whole_building_mode:
            st.caption(
                "Whole-building case: starts from existing contracted income for the property and lets you add realistic extra income on top."
            )
        else:
            st.info(
                "Second-floor-only case: the first floor is assumed to be taken for church use, so the income base is limited mainly to the visible 2nd-floor tenants plus whatever additional income you believe is realistic."
            )
            st.write(
                "Use the visible tenant contracts for the portion expected to remain income-producing, then layer realistic upside only where you believe it can actually continue."
            )

        if space_planner_rental_income > 0:
            st.caption(
                f"Linked from Space Utilization: floors currently marked as rental or mixed contribute a seeded annual rental-income baseline of `{nok(space_planner_rental_income)}`."
            )
        else:
            st.caption(
                "Space Utilization currently contributes no rental-income seed because no non-hall floors are marked as rental or mixed."
            )

        effective_lease_income = contracted_rent * retained_lease_income_pct / 100 * expected_collection_pct / 100
        base_income = effective_lease_income + additional_income

        def net_of_ops(gross: float) -> float:
            return gross * (1 - operating_cost_ratio / 100)

        total_expected_net_income = net_of_ops(base_income)
        coverage = total_expected_net_income / ctx["debt_service"] if ctx["debt_service"] else 0.0
        st.markdown(f"**Total expected annual income:** {nok(base_income)} gross, {nok(total_expected_net_income)} net")
        st.markdown(f"**Debt-service coverage from net income:** {coverage:.2f}x")
        st.caption(
            f"Coverage is measured against the current financing case: bank loan `{nok(ctx['loan_used'])}`, rate `{ctx['nominal_rate']:.2f}%`, term `{ctx['amort_years']}` years."
        )
        if coverage < 1.0:
            st.warning("Base-case income does not fully cover the rough annual debt service.")
        elif coverage < 1.25:
            st.info("Base-case income is positive but still tight against debt service.")
        else:
            st.success("Base-case income gives some room against the rough annual debt service.")

        ctx["income_source"] = income_source
        ctx["whole_building_mode"] = whole_building_mode
        ctx["space_planner_rental_income"] = space_planner_rental_income
        ctx["base_income"] = base_income
        ctx["effective_lease_income"] = effective_lease_income
        ctx["total_expected_net_income"] = total_expected_net_income
        ctx["income_operating_cost_ratio"] = operating_cost_ratio
        ctx["income_coverage"] = coverage
