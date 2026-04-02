from __future__ import annotations

import streamlit as st

from app.finance import first_year_loan_payments
from app.formatting import fmt_m, millions, sidebar_summary_row, signed_m
from app.member_distribution import lookup_known_address_coordinates


def render_sidebar(default, description, label) -> dict:
    ctx: dict = {}
    with st.sidebar:
        st.header(label("sidebar.profile_header", "Portfolio Profile"))
        ctx["organization_name"] = st.text_input(
            label("sidebar.organization_name", "Organization name"),
            value=str(default("profile", "organization_name", "Church organization")),
            help=description("profile", "organization_name", "Name used in scenario captions and summary language throughout the tool."),
        )
        ctx["candidate_building_name"] = st.text_input(
            label("sidebar.candidate_building_name", "Candidate building name"),
            value=str(default("profile", "candidate_building_name", "Candidate building")),
            help=description("profile", "candidate_building_name", "Short working name for the building being evaluated for purchase."),
        )
        ctx["current_building_name"] = st.text_input(
            label("sidebar.current_building_name", "Current building name"),
            value=str(default("profile", "current_building_name", "Current building")),
            help=description("profile", "current_building_name", "Short working name for the building currently occupied or owned."),
        )
        ctx["candidate_building_address"] = st.text_input(
            label("sidebar.candidate_building_address", "Candidate property address"),
            value=str(default("profile", "candidate_building_address", "")),
            help=description("profile", "candidate_building_address", "Street address for the candidate property. This is used in member-geography comparisons and exact property analysis."),
        )
        candidate_known_coords = lookup_known_address_coordinates(ctx["candidate_building_address"])
        candidate_default_lat = candidate_known_coords[0] if candidate_known_coords else float(default("profile", "candidate_building_latitude", 59.9270))
        candidate_default_lon = candidate_known_coords[1] if candidate_known_coords else float(default("profile", "candidate_building_longitude", 10.9120))
        coord_col1, coord_col2 = st.columns(2)
        with coord_col1:
            ctx["candidate_building_latitude"] = st.number_input(
                label("sidebar.candidate_building_latitude", "Candidate lat"),
                value=float(candidate_default_lat),
                step=0.0001,
                format="%.6f",
                help=description("profile", "candidate_building_latitude", "Latitude used for exact property distance analysis. If the address is known in the app, this is prefilled automatically."),
            )
        with coord_col2:
            ctx["candidate_building_longitude"] = st.number_input(
                label("sidebar.candidate_building_longitude", "Candidate lon"),
                value=float(candidate_default_lon),
                step=0.0001,
                format="%.6f",
                help=description("profile", "candidate_building_longitude", "Longitude used for exact property distance analysis. If the address is known in the app, this is prefilled automatically."),
            )
        ctx["candidate_floors"] = st.number_input(
            label("sidebar.candidate_floors", "Candidate floors"),
            min_value=1,
            value=int(default("profile", "candidate_floors", 3)),
            step=1,
            help=description("profile", "candidate_floors", "Number of floors in the candidate building used as a quick screening reference."),
        )
        ctx["candidate_total_area"] = st.number_input(
            label("sidebar.candidate_total_area", "Candidate total area (m2)"),
            min_value=0.0,
            value=float(default("profile", "candidate_total_area", 1_250.0)),
            step=25.0,
            help=description("profile", "candidate_total_area", "Approximate gross internal area of the candidate building used for high-level screening."),
        )

        st.divider()
        st.header(label("sidebar.core_header", "Core Assumptions"))
        st.caption(label("sidebar.core_caption", "Money inputs below are in NOK millions (M) unless marked as % or years."))
        ctx["target_bid"] = st.number_input(
            label("sidebar.target_bid", "Target bid (M)"),
            min_value=0.0,
            value=millions(default("core", "target_bid", 22_000_000)),
            step=0.25,
            format="%.2f",
            help=description("core", "target_bid", "Expected purchase price for the candidate building. Increasing this raises total acquisition cost and increases pressure on financing and renovation headroom."),
        ) * 1_000_000
        ctx["closing_cost_pct"] = st.slider(
            label("sidebar.closing_cost_pct", "Closing costs %"),
            0.0,
            8.0,
            default("core", "closing_cost_pct", 2.5),
            0.1,
            help=description("core", "closing_cost_pct", "Percentage allowance for transaction costs such as legal, fees, and duties. Increasing it reduces cash headroom at closing."),
        )
        ctx["bank_loan"] = st.number_input(
            label("sidebar.bank_loan", "Bank loan available (M)"),
            min_value=0.0,
            value=millions(default("core", "bank_loan", 16_000_000)),
            step=0.25,
            format="%.2f",
            help=description("core", "bank_loan", "Bank loan assumed to be taken in full for the current scenario. Increasing it raises funds at closing and also raises debt service."),
        ) * 1_000_000
        ctx["own_funds"] = st.number_input(
            label("sidebar.own_funds", "Own funds available (M)"),
            min_value=0.0,
            value=millions(default("core", "own_funds", 6_000_000)),
            step=0.25,
            format="%.2f",
            help=description("core", "own_funds", "Equity the church can contribute. Increasing it lowers the funding gap and future debt burden, but ties up more cash immediately."),
        ) * 1_000_000
        ctx["nominal_rate"] = st.number_input(
            label("sidebar.nominal_rate", "Interest rate %"),
            min_value=0.0,
            value=float(default("core", "nominal_rate", 6.85)),
            step=0.05,
            format="%.2f",
            help=description("core", "nominal_rate", "Approximate borrowing rate used in the high-level debt-service estimate. Increasing it raises annual financing pressure."),
        )
        ctx["amort_years"] = st.slider(
            label("sidebar.amort_years", "Amortization years"),
            5,
            30,
            default("core", "amort_years", 20),
            help=description("core", "amort_years", "Repayment period used in the rough debt-service estimate. Shorter periods increase annual payments but reduce debt faster."),
        )

        st.divider()
        st.header(label("sidebar.ministry_header", "Ministry Baseline"))
        use_ministry_baseline = st.checkbox(
            label("sidebar.use_ministry_baseline", "Use ministry baseline to derive free cash"),
            value=default("ministry", "use_ministry_baseline", True),
            help=description("ministry", "use_ministry_baseline", "When enabled, annual free cash is calculated from ministry income minus staff and ministry-running cost rather than typed manually."),
        )
        annual_ministry_income = (
            st.number_input(
                label("sidebar.annual_ministry_income", "Annual ministry income (M)"),
                min_value=0.0,
                value=millions(default("ministry", "annual_ministry_income", 6_750_000)),
                step=0.10,
                format="%.2f",
                help=description("ministry", "annual_ministry_income", "Annual church income before staff and ministry-running costs are deducted."),
            )
            * 1_000_000
        )
        annual_staff_cost = (
            st.number_input(
                label("sidebar.annual_staff_cost", "Annual staff / payroll cost (M)"),
                min_value=0.0,
                value=millions(default("ministry", "annual_staff_cost", 2_900_000)),
                step=0.10,
                format="%.2f",
                help=description("ministry", "annual_staff_cost", "Annual salary and payroll burden for ordinary church operations."),
            )
            * 1_000_000
        )
        annual_ministry_other_cost = (
            st.number_input(
                label("sidebar.annual_ministry_other_cost", "Annual ministry running cost excl. property (M)"),
                min_value=0.0,
                value=millions(default("ministry", "annual_ministry_other_cost", 950_000)),
                step=0.10,
                format="%.2f",
                help=description("ministry", "annual_ministry_other_cost", "Other annual church-service and ministry costs such as consumables, transport, events, and administration before property strategy is considered."),
            )
            * 1_000_000
        )
        derived_annual_member_cashflow = annual_ministry_income - annual_staff_cost - annual_ministry_other_cost
        manual_annual_member_cashflow = (
            st.number_input(
                label("sidebar.manual_annual_member_cashflow", "Manual annual free cash after church operations (M)"),
                min_value=0.0,
                value=millions(default("core", "annual_member_cashflow", max(derived_annual_member_cashflow, 0.0))),
                step=0.10,
                format="%.2f",
                help=description("core", "annual_member_cashflow", "Annual free cash left after normal church staff and operating costs are already covered. This is the amount available to support the property strategy."),
                disabled=use_ministry_baseline,
            )
            * 1_000_000
        )
        ctx["annual_member_cashflow"] = derived_annual_member_cashflow if use_ministry_baseline else manual_annual_member_cashflow

        ctx["acquisition_cost"] = ctx["target_bid"] * (1 + ctx["closing_cost_pct"] / 100)
        ctx["loan_used"] = ctx["bank_loan"]
        ctx["funding_total"] = ctx["loan_used"] + ctx["own_funds"]
        ctx["cash_left_after_acquisition"] = ctx["funding_total"] - ctx["acquisition_cost"]
        ctx["funding_gap"] = max(ctx["acquisition_cost"] - ctx["funding_total"], 0.0)
        ctx["debt_service"] = first_year_loan_payments(
            ctx["loan_used"],
            ctx["nominal_rate"],
            ctx["amort_years"],
            monthly_fee=float(default("mortgage", "monthly_term_fee", 70)),
        )

        st.divider()
        sidebar_summary_row("Acquisition cost", fmt_m(ctx["acquisition_cost"]))
        sidebar_summary_row("Bank loan", fmt_m(ctx["loan_used"]))
        sidebar_summary_row("Own funds", fmt_m(ctx["own_funds"]))
        sidebar_summary_row("Candidate floors", f"{ctx['candidate_floors']}")
        sidebar_summary_row("Candidate total area", f"{ctx['candidate_total_area']:,.0f} m2")
        sidebar_summary_row("Total funds at closing", fmt_m(ctx["funding_total"]))
        sidebar_summary_row(
            "Cash left after acquisition",
            signed_m(ctx["cash_left_after_acquisition"]),
            "available to fund renovation / transition" if ctx["cash_left_after_acquisition"] >= 0 else "extra cash still needed after purchase",
            "#16a34a" if ctx["cash_left_after_acquisition"] >= 0 else "#ef4444",
        )
        sidebar_summary_row("Estimated yearly loan payment", fmt_m(ctx["debt_service"]))
        sidebar_summary_row(
            "Annual free cash after church operations",
            signed_m(ctx["annual_member_cashflow"]),
            "derived from ministry baseline" if use_ministry_baseline else "manual recurring support input",
            "#16a34a" if ctx["annual_member_cashflow"] >= 0 else "#ef4444",
        )

    return ctx
