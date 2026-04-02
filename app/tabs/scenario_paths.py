from __future__ import annotations

import streamlit as st

from app.finance import first_year_loan_payments
from app.formatting import millions, nok, signed_nok


def render_scenario_paths_tab(tab, ctx: dict, default, description) -> None:
    with tab:
        st.subheader("Scenario paths")
        st.caption(
            f"This tab compares the main routes in front of {ctx['organization_name']}: carry both buildings until sale, or sell `{ctx['current_building_name']}`, wait outside `{ctx['candidate_building_name']}` for a period, and rent a larger hall elsewhere while phased work continues."
        )
        st.caption(
            f"Linked in from the current case: `{ctx['candidate_building_name']}` loan `{nok(ctx['loan_used'])}`, `{ctx['candidate_building_name']}` annual running cost `{nok(ctx['grans_annual'])}`, and selected renovation cost `{nok(ctx['selected_renovation_total'])}`."
        )
        annual_member_cashflow = (
            st.number_input(
                "Annual free cash after church operations (M)",
                min_value=0.0,
                value=millions(default("core", "annual_member_cashflow", 0)),
                step=0.10,
                format="%.2f",
                help=description("core", "annual_member_cashflow", "Annual free cash left after normal church staff and operating costs are already covered. This is the amount available to support the property strategy."),
                key="exit_path_annual_cash_flow",
            )
            * 1_000_000
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            alna_sale_price = st.number_input(
                f"{ctx['current_building_name']} sale price",
                min_value=0,
                value=default("exit_path", "alna_sale_price", 25_000_000),
                step=250_000,
                help="Expected gross sale price for the current building in this fallback path.",
            )
            alna_sale_cost_pct = st.slider(
                "Sale cost %",
                0.0,
                10.0,
                float(default("exit_path", "alna_sale_cost_pct", 3.0)),
                0.5,
                help="Broker, legal, and transaction cost deducted from the sale before cash is available.",
            )
            paydown_rule = st.selectbox(
                "Bank paydown on sale",
                [
                    "Repay 75% of outstanding candidate-building loan",
                    "Repay fixed NOK 6M to release collateral",
                ],
                index=0,
                help="Choose the bank outcome to test when the current building is sold.",
            )

        with col2:
            grans_income_waiting = st.number_input(
                f"{ctx['candidate_building_name']} annual property income while waiting",
                min_value=0,
                value=default("exit_path", "grans_income_waiting", int(ctx["base_income"])),
                step=25_000,
                help=f"Expected annual property income while {ctx['organization_name']} is still renting elsewhere and not yet using {ctx['candidate_building_name']} as the main worship site.",
            )
            annual_external_hall_rent = st.number_input(
                "Annual rent for external hall",
                min_value=0,
                value=default("exit_path", "annual_external_hall_rent", 1_200_000),
                step=50_000,
                help=f"Annual rent for the larger hall {ctx['organization_name']} would use instead of moving into {ctx['candidate_building_name']} immediately.",
            )
            annual_rented_hall_staff = st.number_input(
                "Annual staff cost for rented hall",
                min_value=0,
                value=default("exit_path", "annual_rented_hall_staff", 932_757),
                step=25_000,
                help="Annual staff cost tied to using a rented hall, aligned by default to the 2025 staff figure from the General Assembly report.",
            )

        with col3:
            annual_rented_hall_running_cost = st.number_input(
                "Annual consumables / running cost for rented hall",
                min_value=0,
                value=default("exit_path", "annual_rented_hall_running_cost", 150_000),
                step=25_000,
                help="Other annual cost of using a rented hall, such as storage, transport, cleaning, consumables, small equipment, or service charges.",
            )
            annual_reinnovation_spend = st.number_input(
                "Annual renovation / municipality-work budget",
                min_value=0,
                value=default("exit_path", "annual_reinnovation_spend", 1_500_000),
                step=50_000,
                help=f"Annual budget reserved for phased renovation, design work, or negotiations / approvals while {ctx['organization_name']} is not moving into {ctx['candidate_building_name']} yet.",
            )
            years_to_test = st.slider(
                "Years to test",
                1,
                10,
                int(default("exit_path", "years_to_test", 3)),
                help="How many years of this fallback path you want to test.",
            )

        alna_sale_net = alna_sale_price * (1 - alna_sale_cost_pct / 100)
        target_paydown = ctx["loan_used"] * 0.75 if paydown_rule == "Repay 75% of outstanding candidate-building loan" else 6_000_000
        actual_paydown = min(target_paydown, ctx["loan_used"], alna_sale_net)
        loan_after_sale = max(ctx["loan_used"] - actual_paydown, 0.0)
        annual_loan_cost_after_sale = first_year_loan_payments(
            loan_after_sale,
            ctx["nominal_rate"],
            ctx["amort_years"],
            monthly_fee=float(default("mortgage", "monthly_term_fee", 70)),
        )
        sale_cash_left = alna_sale_net - actual_paydown
        one_building_threshold = max(ctx["grans_net"] + ctx["debt_service"], 0.0)
        both_buildings_threshold = max(ctx["grans_net"] + ctx["alna_net"] + ctx["debt_service"], 0.0)

        grans_running_after_income = ctx["grans_annual"] - grans_income_waiting

        def waiting_path_result(reinnovation_factor: float = 1.0, extra_support: float = 0.0) -> dict[str, float | None]:
            route_cost = (
                grans_running_after_income
                + annual_loan_cost_after_sale
                + annual_external_hall_rent
                + annual_rented_hall_staff
                + annual_rented_hall_running_cost
                + annual_reinnovation_spend * reinnovation_factor
            )
            support_total = annual_member_cashflow + extra_support
            annual_gap = support_total - route_cost
            multi_year_gap = route_cost * years_to_test - support_total * years_to_test
            remaining_sale_cash = sale_cash_left - max(multi_year_gap, 0.0)
            runway_years = sale_cash_left / max(-annual_gap, 1.0) if annual_gap < 0 and sale_cash_left > 0 else None
            return {
                "yearly_cost": route_cost,
                "yearly_gap": annual_gap,
                "multi_year_gap": max(multi_year_gap, 0.0),
                "sale_cash_after_run": remaining_sale_cash,
                "runway_years": runway_years,
            }

        base_waiting = waiting_path_result()
        minimum_works_waiting = waiting_path_result(reinnovation_factor=0.5)
        st.markdown("Base waiting path")

        s1, s2, s3, s4 = st.columns(4)
        s1.metric(
            "Cash left from current-building sale",
            nok(sale_cash_left),
            help="Sale proceeds left after sale costs and the chosen bank paydown.",
        )
        s2.metric(
            f"{ctx['candidate_building_name']} loan after sale",
            nok(loan_after_sale),
            help="Remaining candidate-building loan after applying the chosen paydown rule from the current-building sale.",
        )
        s3.metric(
            "Total yearly cost of waiting path",
            nok(base_waiting["yearly_cost"]),
            help="Total yearly cost of keeping the candidate building, paying the reduced loan, renting elsewhere for worship, and continuing phased renovation / municipality work.",
        )
        s4.metric(
            "Yearly cash surplus / gap",
            signed_nok(base_waiting["yearly_gap"]),
            help="Recurring yearly result after comparing the waiting-path cost against the annual free cash left after normal church operations.",
        )

        t1, t2, t3 = st.columns(3)
        t1.metric(
            f"Total {years_to_test}-year gap",
            nok(base_waiting["multi_year_gap"]),
            help=f"Total uncovered cash need over {years_to_test} years if annual cash flow is not enough to carry the fallback path.",
        )
        t2.metric(
            f"Sale cash left after {years_to_test} years",
            signed_nok(base_waiting["sale_cash_after_run"]),
            help=f"Sale cash remaining after covering any recurring shortfall for {years_to_test} years.",
        )
        t3.metric(
            "How long sale cash lasts",
            f"{base_waiting['runway_years']:.1f} years" if base_waiting["runway_years"] is not None else "n/a",
            help="If the fallback path runs an annual gap, this shows roughly how many years the sale cash could cover that gap.",
        )

        st.markdown("Route comparison")
        st.caption("`Yearly cost` includes only the annual carry for that route. It does not include ordinary church staff and ministry-running costs, because those are assumed already covered before the free-cash figure below is entered. In the rented-elsewhere rows, yearly cost means candidate-building running cost after income, yearly loan payment after sale/paydown, external-hall rent, rented-hall staff, rented-hall running cost, and the chosen annual renovation budget.")
        st.caption("`Yearly cash gap / surplus` shows annual free cash after church operations minus yearly cost. `Starting one-time cash` shows the main upfront cash position for that route: bridge cash needed before sale for the overlap route, or sale cash left after selling the current building for the rented-elsewhere routes. `Runway` shows how long that starting cash could cover the yearly gap if the route stays negative.")
        st.caption("`Minimum renovation` assumes only 50% of the annual renovation budget is spent while renting elsewhere.")
        comparison_rows = [
            {
                "route": f"Move into {ctx['candidate_building_name']} with overlap before sale",
                "yearly_cost": both_buildings_threshold,
                "yearly_gap": annual_member_cashflow - both_buildings_threshold,
                "one_time": f"Need {nok(ctx['bridge_shortfall'])} before sale",
                "runway": "n/a",
            },
            {
                "route": f"Sell {ctx['current_building_name']}, rent elsewhere, full renovation",
                "yearly_cost": base_waiting["yearly_cost"],
                "yearly_gap": base_waiting["yearly_gap"],
                "one_time": f"Sale cash {nok(sale_cash_left)}",
                "runway": f"{base_waiting['runway_years']:.1f} years" if base_waiting["runway_years"] is not None else "n/a",
            },
            {
                "route": f"Sell {ctx['current_building_name']}, rent elsewhere, minimum renovation",
                "yearly_cost": minimum_works_waiting["yearly_cost"],
                "yearly_gap": minimum_works_waiting["yearly_gap"],
                "one_time": f"Sale cash {nok(sale_cash_left)}",
                "runway": f"{minimum_works_waiting['runway_years']:.1f} years" if minimum_works_waiting["runway_years"] is not None else "n/a",
            },
        ]
        table_lines = [
            "| Route | Yearly cost | Yearly cash gap / surplus | Starting one-time cash | Runway |",
            "|---|---:|---:|---|---:|",
        ]
        for row in comparison_rows:
            table_lines.append(
                f"| {row['route']} | {nok(row['yearly_cost'])} | {signed_nok(row['yearly_gap'])} | {row['one_time']} | {row['runway']} |"
            )
        st.markdown("\n".join(table_lines))

        if base_waiting["yearly_gap"] >= 0:
            st.success("On these assumptions, the fallback path is recurring-cash-flow positive.")
        elif base_waiting["sale_cash_after_run"] >= 0:
            st.info("On these assumptions, the fallback path has an annual gap, but the current-building sale cash could carry it for the period tested.")
        else:
            st.warning("On these assumptions, the fallback path would still run out of cash unless income improves, rent drops, debt falls further, or renovation is phased more slowly.")

        ctx["annual_member_cashflow_exit_path"] = annual_member_cashflow
        ctx["one_building_threshold"] = one_building_threshold
        ctx["both_buildings_threshold"] = both_buildings_threshold
