from __future__ import annotations

import pandas as pd
import streamlit as st

from app.formatting import nok


def render_income_tab(tab, ctx: dict, default, description, label) -> None:
    with tab:
        st.subheader(label("income.title", "Income generation"))
        st.caption(
            f"Linked from sidebar financing: actual bank loan used `{nok(ctx['loan_used'])}`, rate `{ctx['nominal_rate']:.2f}%`, term `{ctx['amort_years']}` years."
        )
        st.caption(
            label("income.caption", "This model uses the same floor plan as Space Utilization. Turn income on only for floors that can realistically produce it, and leave the others at zero.")
        )

        assembly_floor = int(st.session_state.get("space_assembly_floor", 1))
        retained_lease_income_pct = st.slider("Income likely to continue %", 0.0, 100.0, default("income", "retained_lease_income_pct", 70.0), 1.0, help=description("income", "retained_lease_income_pct", "How much of current lease income survives the transition. Lower values weaken cash support during changeover."))
        expected_collection_pct = st.slider("Cash actually collected %", 0.0, 100.0, default("income", "expected_collection_pct", 95.0), 1.0, help=description("income", "expected_collection_pct", "Expected cash collection quality. Lower values mean income on paper turns into less money in hand."))
        operating_cost_ratio = st.slider("Running-cost share %", 0.0, 80.0, default("income", "operating_cost_ratio", 28.0), 1.0, help=description("income", "operating_cost_ratio", "Share of gross income lost to operating costs. Increasing it reduces the net amount available for debt and project support."))

        floor_income_rows: list[dict[str, float | str | bool]] = []
        for floor_no in range(1, ctx["candidate_floors"] + 1):
            floor_name = f"Floor {floor_no}"
            floor_use = "Assembly floor" if floor_no == assembly_floor else st.session_state.get(f"space_floor_use_{floor_no}", "Support rooms")
            planner_rental_seed = float(st.session_state.get(f"space_floor_rental_income_{floor_no}", 0.0))
            default_income_enabled = floor_no != assembly_floor and (planner_rental_seed > 0 or floor_use in {"Rental", "Mixed / other"})
            with st.expander(f"{floor_name} income model", expanded=default_income_enabled):
                st.caption(f"Space Utilization link: current use tag `{floor_use}`.")
                income_enabled = st.checkbox(
                    f"{floor_name} produces income in this scenario",
                    value=default_income_enabled,
                    key=f"income_enabled_floor_{floor_no}",
                    help="Turn this off for floors that are fully church-use or otherwise not expected to produce income.",
                )
                c1, c2 = st.columns(2)
                with c1:
                    contracted_income = float(
                        st.number_input(
                            f"{floor_name} existing annual contracted income",
                            min_value=0,
                            value=0,
                            step=25_000,
                            key=f"income_contracted_floor_{floor_no}",
                            disabled=not income_enabled,
                            help="Existing lease or contracted income already attached to this floor.",
                        )
                    )
                with c2:
                    additional_income = float(
                        st.number_input(
                            f"{floor_name} additional realistic annual income",
                            min_value=0,
                            value=int(planner_rental_seed),
                            step=25_000,
                            key=f"income_additional_floor_{floor_no}",
                            disabled=not income_enabled,
                            help="Additional realistic income for this floor beyond current contracts, such as retained rent, subletting, or practical shared-use income.",
                        )
                    )
                effective_contract = contracted_income * retained_lease_income_pct / 100 * expected_collection_pct / 100 if income_enabled else 0.0
                floor_total = effective_contract + (additional_income if income_enabled else 0.0)
                floor_income_rows.append(
                    {
                        "floor": floor_name,
                        "use": floor_use,
                        "enabled": income_enabled,
                        "contracted_income": contracted_income if income_enabled else 0.0,
                        "additional_income": additional_income if income_enabled else 0.0,
                        "effective_income": floor_total,
                    }
                )

        floor_income_df = pd.DataFrame(floor_income_rows)
        active_income_df = floor_income_df[floor_income_df["enabled"]].copy()
        base_income = float(active_income_df["effective_income"].sum())
        space_planner_rental_income = float(active_income_df["additional_income"].sum())

        def net_of_ops(gross: float) -> float:
            return gross * (1 - operating_cost_ratio / 100)

        total_expected_net_income = net_of_ops(base_income)
        coverage = total_expected_net_income / ctx["debt_service"] if ctx["debt_service"] else 0.0
        active_floor_count = int(active_income_df["enabled"].sum()) if not active_income_df.empty else 0

        st.markdown(f"### {label('income.sections.summary', 'Income summary')}")
        i1, i2, i3 = st.columns(3)
        i1.metric("Total expected annual income", nok(base_income))
        i2.metric("Net after running cost", nok(total_expected_net_income))
        i3.metric("Debt-service coverage", f"{coverage:.2f}x")
        i4, i5, i6 = st.columns(3)
        i4.metric("Income-producing floors", f"{active_floor_count}/{ctx['candidate_floors']}")
        i5.metric("Retained lease factor", f"{retained_lease_income_pct:.0f}%")
        i6.metric("Collection factor", f"{expected_collection_pct:.0f}%")

        st.caption(
            f"Coverage is measured against the current financing case: bank loan `{nok(ctx['loan_used'])}`, rate `{ctx['nominal_rate']:.2f}%`, term `{ctx['amort_years']}` years."
        )
        if coverage < 1.0:
            st.warning("Base-case income does not fully cover the rough annual debt service.")
        elif coverage < 1.25:
            st.info("Base-case income is positive but still tight against debt service.")
        else:
            st.success("Base-case income gives some room against the rough annual debt service.")
        st.caption(
            label("income.summary_caption", f"Decision-maker reading: this scenario assumes `{active_floor_count}` floor(s) generate income and produces `{nok(total_expected_net_income)}` net after operating cost.")
        )

        floor_income_table = floor_income_df.rename(
            columns={
                "floor": "Floor",
                "use": "Use",
                "enabled": "Income active",
                "contracted_income": "Contracted income",
                "additional_income": "Additional income",
                "effective_income": "Effective income",
            }
        ).copy()
        for column in ["Contracted income", "Additional income", "Effective income"]:
            floor_income_table[column] = floor_income_table[column].map(lambda value: nok(float(value)))
        st.dataframe(floor_income_table, use_container_width=True, hide_index=True)

        ctx["income_source"] = "Floor based"
        ctx["whole_building_mode"] = False
        ctx["space_planner_rental_income"] = space_planner_rental_income
        ctx["base_income"] = base_income
        ctx["effective_lease_income"] = float(active_income_df["contracted_income"].sum()) * retained_lease_income_pct / 100 * expected_collection_pct / 100 if not active_income_df.empty else 0.0
        ctx["total_expected_net_income"] = total_expected_net_income
        ctx["income_operating_cost_ratio"] = operating_cost_ratio
        ctx["income_coverage"] = coverage
