from __future__ import annotations

import streamlit as st

from app.formatting import fmt_m, nok


FIRE_HVAC_SCOPE_OPTIONS = {
    "Existing systems upgrade": {
        "value": 1_500_000,
        "note": "Assumes there is an existing alarm / ventilation base to adapt, extend, and document.",
    },
    "Major adaptation": {
        "value": 2_500_000,
        "note": "Assumes meaningful rework of alarm, ventilation, controls, and compliance items for church use.",
    },
    "Major replacement": {
        "value": 4_500_000,
        "note": "Assumes a much larger replacement / reconfiguration burden, closer to rebuilding major systems.",
    },
}


def render_renovation_tab(tab, ctx: dict, default, description) -> None:
    with tab:
        st.subheader("Renovation / conversion scenarios")
        st.caption(
            f"Linked from sidebar: acquisition cost `{nok(ctx['acquisition_cost'])}`, bank loan `{nok(ctx['loan_used'])}`, and cash left after acquisition `{nok(ctx['cash_left_after_acquisition'])}`."
        )
        col1, col2, col3 = st.columns(3)

        with col1:
            hall_area = st.number_input(
                "Hall area to reinnovate (m2)",
                min_value=0.0,
                value=float(default("renovation", "hall_area", 420.0)),
                step=10.0,
                help=description("renovation", "hall_area", "Estimated area to convert into the main hall zone. Increasing it raises cost, but may also improve capacity and usefulness."),
            )
            hall_light = st.number_input("Light hall work cost per m2", min_value=0, value=default("renovation", "hall_light", 4_500), step=250, help=description("renovation", "hall_light", "Low-cost hall adaptation rate. Increasing it raises the light scenario total."))
            hall_medium = st.number_input("Medium hall work cost per m2", min_value=0, value=default("renovation", "hall_medium", 8_500), step=250, help=description("renovation", "hall_medium", "Mid-range hall conversion rate. Increasing it raises the mid scenario total."))
            hall_heavy = st.number_input("Heavy hall work cost per m2", min_value=0, value=default("renovation", "hall_heavy", 13_500), step=250, help=description("renovation", "hall_heavy", "High intervention hall rate for more serious rebuilding and systems work."))
            fire_hvac_scope = st.selectbox(
                "Fire / alarm / ventilation scope",
                list(FIRE_HVAC_SCOPE_OPTIONS.keys()),
                index=1,
                help="Use this to choose whether the building likely needs mainly system upgrades, major adaptation, or major replacement. The recent photos suggest there is an existing alarm and ventilation base, so this is not automatically a blank-slate install.",
            )
            use_scope_based_fire_hvac = st.checkbox(
                "Use suggested fire / alarm / ventilation amount",
                value=True,
                help="When enabled, the lump sum follows the selected scope. Turn it off if you want to enter your own amount.",
            )
            scope_value = FIRE_HVAC_SCOPE_OPTIONS[fire_hvac_scope]["value"]
            if use_scope_based_fire_hvac:
                fixed_fire_hvac = scope_value
                st.metric("Suggested lump sum", fmt_m(fixed_fire_hvac))
            else:
                fixed_fire_hvac = st.number_input(
                    "Fire / alarm / ventilation / compliance lump sum",
                    min_value=0,
                    value=default("renovation", "fixed_fire_hvac", 2_500_000),
                    step=100_000,
                    help=description("renovation", "fixed_fire_hvac", "Allowance for ventilation, fire, code, and compliance-heavy work. Increasing it materially raises total project cost."),
                )
            st.caption(FIRE_HVAC_SCOPE_OPTIONS[fire_hvac_scope]["note"])
            specialist_fees_pct = st.slider("Professional fees %", 0.0, 20.0, default("renovation", "specialist_fees_pct", 8.0), 0.5, help=description("renovation", "specialist_fees_pct", "Architect, engineer, consultant, and similar professional costs. Higher values increase every renovation scenario."))

        with col2:
            office_area = st.number_input(
                "Office / classroom area to reinnovate (m2)",
                min_value=0.0,
                value=float(default("renovation", "office_area", 300.0)),
                step=10.0,
                help=description("renovation", "office_area", "Estimated office, classroom, or weekday-use area to improve. Increasing it raises cost but can increase flexibility and income options."),
            )
            office_light = st.number_input("Light office / classroom work cost per m2", min_value=0, value=default("renovation", "office_light", 2_500), step=250, help=description("renovation", "office_light", "Low-cost office/classroom rate."))
            office_medium = st.number_input("Medium office / classroom work cost per m2", min_value=0, value=default("renovation", "office_medium", 5_500), step=250, help=description("renovation", "office_medium", "Mid-range office/classroom rate."))
            office_heavy = st.number_input("Heavy office / classroom work cost per m2", min_value=0, value=default("renovation", "office_heavy", 8_500), step=250, help=description("renovation", "office_heavy", "High intervention office/classroom rate."))
            technical_catchup = st.number_input(
                "Technical catch-up lump sum",
                min_value=0,
                value=default("renovation", "technical_catchup", 1_000_000),
                step=100_000,
                help=description("renovation", "technical_catchup", "Allowance for roof, drainage, electrical, water ingress, and other base-building issues that are not part of room fit-out."),
            )
            contingency_pct = st.slider("Contingency %", 0.0, 30.0, default("renovation", "contingency_pct", 15.0), 0.5, help=description("renovation", "contingency_pct", "Reserve for surprises and omissions. Higher values increase budget but lower the chance of being underfunded."))

        with col3:
            basement_area = st.number_input(
                "Basement / support area to reinnovate (m2)",
                min_value=0.0,
                value=float(default("renovation", "basement_area", 200.0)),
                step=10.0,
                help=description("renovation", "basement_area", "Estimated basement or support-space area to improve. Increasing it raises cost but may improve storage and back-of-house operations."),
            )
            basement_light = st.number_input("Light basement work cost per m2", min_value=0, value=default("renovation", "basement_light", 1_500), step=250, help=description("renovation", "basement_light", "Low-cost basement/support-space rate."))
            basement_medium = st.number_input("Medium basement work cost per m2", min_value=0, value=default("renovation", "basement_medium", 3_500), step=250, help=description("renovation", "basement_medium", "Mid-range basement/support-space rate."))
            basement_heavy = st.number_input("Heavy basement work cost per m2", min_value=0, value=default("renovation", "basement_heavy", 5_500), step=250, help=description("renovation", "basement_heavy", "High intervention basement/support-space rate."))
            tenant_turnover = st.number_input(
                "Tenant turnover / strip-out / adaptation",
                min_value=0,
                value=default("renovation", "tenant_turnover", 500_000),
                step=50_000,
                help=description("renovation", "tenant_turnover", "Allowance for making areas usable after tenant change, demolition, strip-out, partitions, cleaning, and practical adaptation work."),
            )
            site_parking = st.number_input(
                "Site / parking / access works",
                min_value=0,
                value=default("renovation", "site_parking", 250_000),
                step=50_000,
                help=description("renovation", "site_parking", "Allowance for outdoor works, access improvements, markings, lighting, or other site-related upgrades."),
            )
            furniture_av = st.number_input("Furniture / AV / loose fit-out", min_value=0, value=default("renovation", "furniture_av", 1_250_000), step=50_000, help=description("renovation", "furniture_av", "Allowance for chairs, AV, loose furniture, and non-building fit-out items."))

        def build_components(hall_rate: float, office_rate: float, basement_rate: float) -> dict[str, float]:
            area_work = hall_area * hall_rate + office_area * office_rate + basement_area * basement_rate
            direct_cost = area_work + fixed_fire_hvac + technical_catchup + tenant_turnover + site_parking + furniture_av
            fees = area_work * specialist_fees_pct / 100
            contingency = (direct_cost + fees) * contingency_pct / 100
            total = direct_cost + fees + contingency
            total_area = hall_area + office_area + basement_area
            return {
                "area_work": area_work,
                "fees": fees,
                "fire_hvac": fixed_fire_hvac,
                "technical_catchup": technical_catchup,
                "tenant_turnover": tenant_turnover,
                "site_parking": site_parking,
                "furniture_av": furniture_av,
                "contingency": contingency,
                "total": total,
                "cost_per_m2": total / total_area if total_area else 0.0,
            }

        def build_total(hall_rate: float, office_rate: float, basement_rate: float) -> float:
            base = hall_area * hall_rate + office_area * office_rate + basement_area * basement_rate
            fees = base * specialist_fees_pct / 100
            contingency = (
                base
                + fees
                + fixed_fire_hvac
                + technical_catchup
                + tenant_turnover
                + site_parking
                + furniture_av
            ) * contingency_pct / 100
            return (
                base
                + fees
                + fixed_fire_hvac
                + technical_catchup
                + tenant_turnover
                + site_parking
                + furniture_av
                + contingency
            )

        low_total = build_total(hall_light, office_light, basement_light)
        mid_total = build_total(hall_medium, office_medium, basement_medium)
        high_total = build_total(hall_heavy, office_heavy, basement_heavy)
        low_components = build_components(hall_light, office_light, basement_light)
        mid_components = build_components(hall_medium, office_medium, basement_medium)
        high_components = build_components(hall_heavy, office_heavy, basement_heavy)

        c1, c2, c3 = st.columns(3)
        c1.metric("Light scenario", fmt_m(low_total))
        c2.metric("Mid scenario", fmt_m(mid_total))
        c3.metric("Heavy scenario", fmt_m(high_total))

        scenario_choice = st.selectbox(
            "Working renovation scenario",
            ["Light", "Mid", "Heavy"],
            index=1,
            help="Choose the renovation scenario you want to carry into the transition bridge calculation.",
        )
        scenario_totals = {
            "Light": low_total,
            "Mid": mid_total,
            "Heavy": high_total,
        }
        scenario_components = {
            "Light": low_components,
            "Mid": mid_components,
            "Heavy": high_components,
        }
        selected_renovation_total = scenario_totals[scenario_choice]
        selected_components = scenario_components[scenario_choice]

        renovation_funding_needed = max(selected_renovation_total - max(ctx["cash_left_after_acquisition"], 0.0), 0.0)

        r1, r2, r3 = st.columns(3)
        r1.metric("Cash left after acquisition", nok(ctx["cash_left_after_acquisition"]))
        r2.metric(f"Selected total renovation cost ({scenario_choice})", fmt_m(selected_renovation_total))
        r3.metric("Extra funding needed for renovation", fmt_m(renovation_funding_needed))

        ctx["selected_renovation_total"] = selected_renovation_total
        ctx["selected_renovation_components"] = selected_components
        ctx["renovation_funding_needed"] = renovation_funding_needed
