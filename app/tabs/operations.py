from __future__ import annotations

import streamlit as st

from app.formatting import clamp_index, nok


def render_operations_tab(tab, ctx: dict, default, description) -> None:
    with tab:
        st.subheader("Portfolio overlap and inflation")
        st.caption(
            f"Use this tab to test what happens if `{ctx['candidate_building_name']}` starts running before `{ctx['current_building_name']}` is sold, creating overlapping property costs."
        )
        st.caption(
            f"Linked inputs in use here: property-income assumptions from the Income tab and financing pressure from the sidebar debt case `{nok(ctx['debt_service'])}` per year."
        )

        linked_grans_income = ctx["base_income"]
        operating_inflation_pct = st.slider(
            "Annual inflation on current-building operating cost %",
            0.0,
            12.0,
            float(default("operations", "current_building_inflation_pct", 3.0)),
            0.1,
            help="Use this to grow the current-building annual running cost if overlap lasts and inflation pressure continues.",
        )
        left_building, divider, right_building = st.columns([1, 0.06, 1])
        with left_building:
            st.markdown(f"**{ctx['candidate_building_name']}**")
            g1, g2 = st.columns(2)
            with g1:
                grans_utilities = st.number_input("Electricity / internet", min_value=0, value=default("operations", "grans_utilities", 350_000), step=10_000, help=description("operations", "grans_utilities", "Projected candidate-building cost for electricity, heating, internet, and similar utilities. Increasing it raises operating pressure."))
                grans_municipal = st.number_input("Municipal / water / sewage", min_value=0, value=default("operations", "grans_municipal", 120_000), step=10_000, help=description("operations", "grans_municipal", "Projected candidate-building cost for municipal charges, water, and sewage. Increasing it raises annual building carrying cost."))
                grans_accounting = st.number_input("Auditor / accounting", min_value=0, value=default("operations", "grans_accounting", 100_000), step=10_000, help=description("operations", "grans_accounting", "Projected candidate-building accounting, audit, or finance administration cost."))
                grans_insurance = st.number_input("Building insurance", min_value=0, value=default("operations", "grans_insurance", 180_000), step=10_000, help=description("operations", "grans_insurance", "Projected building-insurance cost for the candidate building."))
                grans_security = st.number_input("Security / control", min_value=0, value=default("operations", "grans_security", 40_000), step=10_000, help=description("operations", "grans_security", "Projected candidate-building cost for security, alarms, and basic safety/control systems."))
            with g2:
                grans_maintenance = st.number_input("Minor maintenance", min_value=0, value=default("operations", "grans_maintenance", 150_000), step=10_000, help=description("operations", "grans_maintenance", "Projected candidate-building cost for minor repairs, replacement, and upkeep."))
                grans_cleaning = st.number_input("Cleaning / consumables", min_value=0, value=default("operations", "grans_cleaning", 70_000), step=10_000, help=description("operations", "grans_cleaning", "Projected candidate-building cost for cleaning supplies and routine consumables."))
                grans_caretaker = st.number_input("Caretaker / snow / outdoor", min_value=0, value=default("operations", "grans_caretaker", 180_000), step=10_000, help=description("operations", "grans_caretaker", "Projected candidate-building cost for caretaker, snow clearing, and outdoor maintenance."))
                grans_other = st.number_input("Other building costs", min_value=0, value=default("operations", "grans_other", 100_000), step=10_000, help=description("operations", "grans_other", "Any additional candidate-building cost not already listed."))
                grans_contingency = st.number_input("Operating contingency", min_value=0, value=default("operations", "grans_contingency", 100_000), step=10_000, help=description("operations", "grans_contingency", "Extra annual buffer for candidate-building operating surprises. Increasing it raises prudence and cost at the same time."))
                grans_income = st.number_input(
                    "Annual property income",
                    min_value=0,
                    value=default("operations", "grans_income_override", int(linked_grans_income)),
                    step=25_000,
                    help="Yearly candidate-building property income used in this tab. It is prefilled from the Income tab, but you can adjust it here if you want a different operating-case assumption.",
                )
        with divider:
            st.markdown(
                """
                <div style="border-left:2px solid #d1d5db; height:100%; min-height:520px; margin:0 auto;"></div>
                """,
                unsafe_allow_html=True,
            )
        with right_building:
            st.markdown(f"**{ctx['current_building_name']}**")
            a1, a2 = st.columns(2)
            with a1:
                alna_utilities = st.number_input("Electricity / internet", min_value=0, value=default("operations", "alna_utilities", 150_000), step=10_000, help=description("operations", "alna_utilities", "Report-based Alnafetgata cost for electricity, phone, and internet."))
                alna_municipal = st.number_input("Municipal / water / sewage", min_value=0, value=default("operations", "alna_municipal", 85_000), step=10_000, help=description("operations", "alna_municipal", "Report-based Alnafetgata cost for taxes, municipal charges, water, and sewage."))
                alna_accounting = st.number_input("Auditor / accounting", min_value=0, value=default("operations", "alna_accounting", 85_000), step=10_000, help=description("operations", "alna_accounting", "Report-based Alnafetgata cost for external auditor and accounting support."))
                alna_insurance = st.number_input("Building insurance", min_value=0, value=default("operations", "alna_insurance", 106_000), step=10_000, help=description("operations", "alna_insurance", "Report-based Alnafetgata building-insurance cost."))
                alna_security = st.number_input("Security / control", min_value=0, value=default("operations", "alna_security", 25_000), step=5_000, help=description("operations", "alna_security", "Report-style Alnafetgata cost for building security and control."))
                alna_staff = st.number_input(
                    "Staff / payroll",
                    min_value=0,
                    value=default("operations", "alna_staff", 932_757),
                    step=25_000,
                    help="Annual staff cost attributed to Alnafetgata. Seeded from the 2025 actual salary figure visible in the General Assembly 2025 Report and 2026 Plan PDF. This is wages only, not payroll tax or employee insurance.",
                )
            with a2:
                alna_maintenance = st.number_input("Minor maintenance", min_value=0, value=default("operations", "alna_maintenance", 50_000), step=10_000, help=description("operations", "alna_maintenance", "Report-style Alnafetgata cost for minor maintenance and replacements."))
                alna_cleaning = st.number_input("Cleaning / consumables", min_value=0, value=default("operations", "alna_cleaning", 50_000), step=10_000, help=description("operations", "alna_cleaning", "Report-style Alnafetgata cost for cleaning and consumable supplies."))
                alna_caretaker = st.number_input("Caretaker / snow / outdoor", min_value=0, value=default("operations", "alna_caretaker", 150_000), step=10_000, help=description("operations", "alna_caretaker", "Report-style Alnafetgata cost for caretaker, snow clearing, and outdoor work."))
                alna_other = st.number_input("Other building costs", min_value=0, value=default("operations", "alna_other", 50_000), step=10_000, help=description("operations", "alna_other", "Any additional Alnafetgata building cost not already listed."))
                alna_contingency = st.number_input("Operating contingency", min_value=0, value=default("operations", "alna_contingency", 50_000), step=10_000, help=description("operations", "alna_contingency", "Extra annual buffer for Alnafetgata operating surprises. Increasing it raises prudence and cost at the same time."))
                alna_income = st.number_input("Annual property income", min_value=0, value=default("operations", "alna_income", 0), step=25_000, help=description("operations", "alna_income", "Annual property-related income still generated by Alnafetgata 2 during overlap."))

        overlap_months = st.slider("Months both buildings run in parallel", 0, 36, default("operations", "overlap_months", 9), help=description("operations", "overlap_months", "How long both sites must be carried at the same time. Increasing it raises temporary double-running pressure."))
        duplicate_staffing = st.number_input("Extra overlap admin / staffing cost", min_value=0, value=default("operations", "duplicate_staffing", 180_000), step=25_000, help=description("operations", "duplicate_staffing", "Extra staffing or management cost caused by running both properties during transition."))
        moving_cost = st.number_input("One-off moving / transition cost", min_value=0, value=default("operations", "moving_cost", 300_000), step=25_000, help=description("operations", "moving_cost", "One-time moving and transition cost."))
        overlap_income_offset = st.number_input(
            "Income offset during overlap (temporary rent / hall use / subletting)",
            min_value=0,
            value=default("operations", "overlap_income_offset", 0),
            step=25_000,
            help=description("operations", "overlap_income_offset", "Additional temporary income that offsets overlap pressure but is not already counted in the building income fields."),
        )

        grans_annual = (
            grans_utilities
            + grans_municipal
            + grans_accounting
            + grans_insurance
            + grans_security
            + grans_maintenance
            + grans_cleaning
            + grans_caretaker
            + grans_other
            + grans_contingency
        )
        alna_annual = (
            alna_utilities
            + alna_municipal
            + alna_accounting
            + alna_insurance
            + alna_security
            + alna_staff
            + alna_maintenance
            + alna_cleaning
            + alna_caretaker
            + alna_other
            + alna_contingency
        )
        inflation_factor = (1 + operating_inflation_pct / 100) ** (overlap_months / 12) if overlap_months > 0 else 1.0
        alna_annual_inflated = alna_annual * inflation_factor
        annual_combined = grans_annual + alna_annual_inflated
        annual_property_income = grans_income + alna_income
        grans_net = grans_annual - grans_income
        alna_net = alna_annual_inflated - alna_income
        overlap_cost = (
            (annual_combined - annual_property_income) * (overlap_months / 12)
            + duplicate_staffing
            + moving_cost
            - overlap_income_offset
        )
        overlap_cost = max(overlap_cost, 0.0)

        s1, s2, s3 = st.columns(3)
        s1.metric(
            f"{ctx['candidate_building_name']} annual running cost",
            nok(grans_annual),
            help="Total yearly candidate-building cost before subtracting any property income.",
        )
        s2.metric(
            f"{ctx['current_building_name']} annual running cost",
            nok(alna_annual_inflated),
            help="Total yearly current-building cost before subtracting any property income, including overlap-period inflation.",
        )
        s3.metric(
            "Total yearly cost after income",
            nok(grans_net + alna_net),
            help="The yearly carrying cost of both buildings together after subtracting property income from both.",
        )

        st.write(
            f"This is the extra planning pressure if `{ctx['current_building_name']}` does not sell quickly and both properties must be carried at the same time."
        )

        if overlap_months == 0:
            st.success("No overlap period assumed.")
        elif overlap_months <= 6:
            st.info("Short overlap assumed. This is still material but more manageable.")
        else:
            st.warning("Long overlap assumed. Double-running costs can become a major cash-flow issue.")

        bridge_months = overlap_months
        if ctx["include_sale_prepayment"] and ctx["sale_delay_months"] > 0:
            bridge_months = min(overlap_months, ctx["sale_delay_months"])
        schedule = ctx["mortgage_schedule"]
        overlap_schedule = schedule[: clamp_index(bridge_months - 1, len(schedule)) + 1] if schedule and bridge_months > 0 else []
        debt_service_during_overlap = (
            sum(item["principal_payment"] + item["interest_payment"] + item["monthly_fee"] for item in overlap_schedule)
            if overlap_schedule
            else 0.0
        )
        renovation_spend_before_sale = ctx["selected_renovation_total"]
        cash_left_after_closing = ctx["cash_left_after_acquisition"]
        bridge_cash_need = overlap_cost + debt_service_during_overlap + renovation_spend_before_sale
        bridge_shortfall = bridge_cash_need - max(cash_left_after_closing, 0.0)

        st.markdown("Bridge period before current-building sale")
        st.caption(
            f"This view combines three cash burdens that can hit at the same time: double-running cost, loan payments during the overlap months, and the selected renovation package to be funded before `{ctx['current_building_name']}` is sold."
        )
        if bridge_months != overlap_months:
            st.caption(
                f"Loan payments before sale are currently counted for `{bridge_months}` months because the mortgage plan assumes sale in month `{ctx['sale_delay_months']}`."
            )

        b1, b2, b3, b4 = st.columns(4)
        b1.metric(
            "Overlap cost before sale",
            nok(overlap_cost),
            help="Extra operating cost from carrying both buildings at the same time before the current building is sold.",
        )
        b2.metric(
            "Loan payments before sale",
            nok(debt_service_during_overlap),
            help="Loan payments that fall due before the old building is sold. If the mortgage plan assumes sale earlier than the overlap period ends, only the months before sale are counted here.",
        )
        b3.metric(
            "Total cash needed before sale",
            nok(bridge_cash_need),
            help="Combined cash need before sale from overlap cost, loan payments before sale, and the selected renovation package.",
        )
        b4.metric(
            "Extra cash still needed before sale",
            nok(bridge_shortfall),
            help="How much extra cash is still needed after using cash left from acquisition toward the total cash needed before sale.",
        )

        ctx["operating_inflation_pct"] = operating_inflation_pct
        ctx["grans_annual"] = grans_annual
        ctx["alna_annual_inflated"] = alna_annual_inflated
        ctx["grans_net"] = grans_net
        ctx["alna_net"] = alna_net
        ctx["overlap_months"] = overlap_months
        ctx["overlap_cost"] = overlap_cost
        ctx["debt_service_during_overlap"] = debt_service_during_overlap
        ctx["renovation_spend_before_sale"] = renovation_spend_before_sale
        ctx["bridge_shortfall"] = bridge_shortfall
