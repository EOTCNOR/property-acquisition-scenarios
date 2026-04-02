from __future__ import annotations

import pandas as pd
import streamlit as st

from app.formatting import fmt_m, nok


FIRE_HVAC_SCOPE_OPTIONS = {
    "Existing systems upgrade": {
        "value": 1_500_000,
        "note": "Assumes there is an existing alarm / ventilation base to adapt, extend, and document.",
    },
    "Major adaptation": {
        "value": 2_500_000,
        "note": "Assumes meaningful rework of alarm, ventilation, controls, and compliance items for the intended use.",
    },
    "Major replacement": {
        "value": 4_500_000,
        "note": "Assumes a much larger replacement / reconfiguration burden, closer to rebuilding major systems.",
    },
}


def _default_floor_area(ctx: dict, floor_no: int) -> float:
    width = float(st.session_state.get(f"space_floor_width_{floor_no}", 0.0))
    length = float(st.session_state.get(f"space_floor_length_{floor_no}", 0.0))
    measured_area = width * length
    if measured_area > 0:
        return measured_area
    return max(float(ctx["candidate_total_area"]) / max(int(ctx["candidate_floors"]), 1), 0.0)


def _seed_floor_rates(ctx: dict, default, floor_no: int) -> tuple[int, int, int]:
    assembly_floor = int(st.session_state.get("space_assembly_floor", 1))
    if floor_no == assembly_floor:
        return (
            int(default("renovation", "hall_light", 4_500)),
            int(default("renovation", "hall_medium", 8_500)),
            int(default("renovation", "hall_heavy", 13_500)),
        )
    return (
        int(default("renovation", "office_light", 2_500)),
        int(default("renovation", "office_medium", 5_500)),
        int(default("renovation", "office_heavy", 8_500)),
    )


def render_renovation_tab(tab, ctx: dict, default, description, label) -> None:
    with tab:
        st.subheader(label("renovation.title", "Renovation / conversion scenarios"))
        st.caption(
            f"Linked from sidebar: acquisition cost `{nok(ctx['acquisition_cost'])}`, bank loan `{nok(ctx['loan_used'])}`, and cash left after acquisition `{nok(ctx['cash_left_after_acquisition'])}`."
        )
        st.caption(
            label("renovation.caption", "This model now follows the same floor logic as Space Utilization. Decide which floors are in scope, what area is being touched on each floor, and then add the building-wide items that decision makers should see separately.")
        )

        floor_rows: list[dict[str, float | int | str | bool]] = []
        assembly_floor = int(st.session_state.get("space_assembly_floor", 1))
        for floor_no in range(1, ctx["candidate_floors"] + 1):
            floor_use = st.session_state.get(f"space_floor_use_{floor_no}", "Support rooms")
            floor_name = f"Floor {floor_no}"
            measured_area = _default_floor_area(ctx, floor_no)
            default_light, default_mid, default_heavy = _seed_floor_rates(ctx, default, floor_no)
            with st.expander(f"{floor_name} renovation model", expanded=floor_no == assembly_floor):
                st.caption(
                    f"Space Utilization link: measured area seed `{measured_area:,.0f} m2`; current use tag `{floor_use}`."
                )
                include_floor = st.checkbox(
                    f"Include {floor_name} in renovation model",
                    value=True,
                    key=f"renovation_include_floor_{floor_no}",
                    help="Turn this off if this floor is outside the current renovation scope.",
                )
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    renovation_area = st.number_input(
                        f"{floor_name} renovation area (m2)",
                        min_value=0.0,
                        value=float(measured_area),
                        step=10.0,
                        key=f"renovation_area_floor_{floor_no}",
                        help="Area on this floor expected to be renovated or reconfigured in the current plan.",
                    )
                with c2:
                    light_rate = st.number_input(
                        f"{floor_name} light cost per m2",
                        min_value=0,
                        value=default_light,
                        step=250,
                        key=f"renovation_light_rate_floor_{floor_no}",
                        help="Lower-cost rate for lighter intervention on this floor.",
                    )
                with c3:
                    mid_rate = st.number_input(
                        f"{floor_name} mid cost per m2",
                        min_value=0,
                        value=default_mid,
                        step=250,
                        key=f"renovation_mid_rate_floor_{floor_no}",
                        help="Working mid-range renovation rate for this floor.",
                    )
                with c4:
                    heavy_rate = st.number_input(
                        f"{floor_name} heavy cost per m2",
                        min_value=0,
                        value=default_heavy,
                        step=250,
                        key=f"renovation_heavy_rate_floor_{floor_no}",
                        help="Higher-intervention rate for more serious rebuilding or compliance-heavy work on this floor.",
                    )
                floor_rows.append(
                    {
                        "floor": floor_name,
                        "use": "Assembly floor" if floor_no == assembly_floor else floor_use,
                        "included": include_floor,
                        "area": renovation_area,
                        "light_total": renovation_area * light_rate if include_floor else 0.0,
                        "mid_total": renovation_area * mid_rate if include_floor else 0.0,
                        "heavy_total": renovation_area * heavy_rate if include_floor else 0.0,
                    }
                )

        st.markdown(f"#### {label('renovation.sections.shared_items', 'Building-wide items')}")
        col1, col2, col3 = st.columns(3)
        with col1:
            fire_hvac_scope = st.selectbox(
                "Fire / alarm / ventilation scope",
                list(FIRE_HVAC_SCOPE_OPTIONS.keys()),
                index=1,
                help="Choose the broad building-wide fire / alarm / ventilation burden to apply across the project.",
            )
            use_scope_based_fire_hvac = st.checkbox(
                "Use suggested fire / alarm / ventilation amount",
                value=True,
                help="When enabled, the lump sum follows the selected scope. Turn it off to enter your own number.",
            )
            scope_value = FIRE_HVAC_SCOPE_OPTIONS[fire_hvac_scope]["value"]
            if use_scope_based_fire_hvac:
                fixed_fire_hvac = float(scope_value)
                st.metric("Suggested fire / ventilation amount", fmt_m(fixed_fire_hvac))
            else:
                fixed_fire_hvac = float(
                    st.number_input(
                        "Fire / alarm / ventilation lump sum",
                        min_value=0,
                        value=int(default("renovation", "fixed_fire_hvac", 2_500_000)),
                        step=100_000,
                        help=description("renovation", "fixed_fire_hvac", "Allowance for ventilation, fire, code, and compliance-heavy work. Increasing it materially raises total project cost."),
                    )
                )
            st.caption(FIRE_HVAC_SCOPE_OPTIONS[fire_hvac_scope]["note"])
            electrical_upgrade = float(
                st.number_input(
                    "Electrical / EL upgrade lump sum",
                    min_value=0,
                    value=600_000,
                    step=50_000,
                    help="Building-wide allowance for panel upgrades, rewiring, lighting, controls, and related electrical work.",
                )
            )
            specialist_fees_pct = st.slider("Professional fees %", 0.0, 20.0, default("renovation", "specialist_fees_pct", 8.0), 0.5, help=description("renovation", "specialist_fees_pct", "Architect, engineer, consultant, and similar professional costs. Higher values increase every renovation scenario."))

        with col2:
            technical_catchup = float(
                st.number_input(
                    "Technical catch-up lump sum",
                    min_value=0,
                    value=int(default("renovation", "technical_catchup", 1_000_000)),
                    step=100_000,
                    help=description("renovation", "technical_catchup", "Allowance for roof, drainage, electrical, water ingress, and other base-building issues that are not part of room fit-out."),
                )
            )
            tenant_turnover = float(
                st.number_input(
                    "Tenant turnover / strip-out / adaptation",
                    min_value=0,
                    value=int(default("renovation", "tenant_turnover", 500_000)),
                    step=50_000,
                    help=description("renovation", "tenant_turnover", "Allowance for making areas usable after tenant change, demolition, strip-out, partitions, cleaning, and practical adaptation work."),
                )
            )
            site_parking = float(
                st.number_input(
                    "Site / parking / access works",
                    min_value=0,
                    value=int(default("renovation", "site_parking", 250_000)),
                    step=50_000,
                    help=description("renovation", "site_parking", "Allowance for outdoor works, access improvements, markings, lighting, or other site-related upgrades."),
                )
            )
            contingency_pct = st.slider("Contingency %", 0.0, 30.0, default("renovation", "contingency_pct", 15.0), 0.5, help=description("renovation", "contingency_pct", "Reserve for surprises and omissions. Higher values increase budget but lower the chance of being underfunded."))

        with col3:
            furniture_av = float(
                st.number_input(
                    "Furniture / AV / loose fit-out",
                    min_value=0,
                    value=int(default("renovation", "furniture_av", 1_250_000)),
                    step=50_000,
                    help=description("renovation", "furniture_av", "Allowance for chairs, AV, loose furniture, and non-building fit-out items."),
                )
            )
            common_it_security = float(
                st.number_input(
                    "Common IT / access / security systems",
                    min_value=0,
                    value=250_000,
                    step=25_000,
                    help="Building-wide allowance for internet, access control, CCTV, alarms, and shared technology systems beyond loose AV.",
                )
            )

        floors_df = pd.DataFrame(floor_rows)
        included_floors = floors_df[floors_df["included"]].copy()
        area_work_light = float(included_floors["light_total"].sum())
        area_work_mid = float(included_floors["mid_total"].sum())
        area_work_heavy = float(included_floors["heavy_total"].sum())
        shared_items_total = fixed_fire_hvac + electrical_upgrade + technical_catchup + tenant_turnover + site_parking + furniture_av + common_it_security

        def build_components(area_work: float) -> dict[str, float]:
            fees = area_work * specialist_fees_pct / 100
            direct_cost = area_work + shared_items_total
            contingency = (direct_cost + fees) * contingency_pct / 100
            total = direct_cost + fees + contingency
            total_area = float(included_floors["area"].sum())
            return {
                "area_work": area_work,
                "fire_hvac": fixed_fire_hvac,
                "electrical_upgrade": electrical_upgrade,
                "technical_catchup": technical_catchup,
                "tenant_turnover": tenant_turnover,
                "site_parking": site_parking,
                "furniture_av": furniture_av,
                "common_it_security": common_it_security,
                "fees": fees,
                "contingency": contingency,
                "total": total,
                "cost_per_m2": total / total_area if total_area else 0.0,
            }

        light_components = build_components(area_work_light)
        mid_components = build_components(area_work_mid)
        heavy_components = build_components(area_work_heavy)
        scenario_components = {
            "Light": light_components,
            "Mid": mid_components,
            "Heavy": heavy_components,
        }

        c1, c2, c3 = st.columns(3)
        c1.metric("Light scenario", fmt_m(light_components["total"]))
        c2.metric("Mid scenario", fmt_m(mid_components["total"]))
        c3.metric("Heavy scenario", fmt_m(heavy_components["total"]))

        scenario_choice = st.selectbox(
            "Working renovation scenario",
            ["Light", "Mid", "Heavy"],
            index=1,
            help="Choose the renovation scenario you want to carry into the transition bridge calculation.",
        )
        selected_components = scenario_components[scenario_choice]
        selected_renovation_total = selected_components["total"]
        renovation_funding_needed = max(selected_renovation_total - max(ctx["cash_left_after_acquisition"], 0.0), 0.0)
        included_floor_count = int(included_floors["included"].sum()) if not included_floors.empty else 0
        included_area = float(included_floors["area"].sum()) if not included_floors.empty else 0.0
        shared_share = selected_components["total"] - selected_components["area_work"]

        st.markdown(f"### {label('renovation.sections.summary', 'Renovation summary')}")
        r1, r2, r3 = st.columns(3)
        r1.metric("Cash left after acquisition", nok(ctx["cash_left_after_acquisition"]))
        r2.metric(f"Selected total renovation cost ({scenario_choice})", fmt_m(selected_renovation_total))
        r3.metric("Extra funding needed for renovation", fmt_m(renovation_funding_needed))
        r4, r5, r6 = st.columns(3)
        r4.metric("Floors in scope", f"{included_floor_count}/{ctx['candidate_floors']}")
        r5.metric("Renovation area in scope", f"{included_area:,.0f} m2")
        r6.metric("Selected cost per m2", nok(selected_components["cost_per_m2"]))
        st.caption(
            label("renovation.summary_caption", f"Decision-maker reading: the `{scenario_choice}` scenario assumes `{fmt_m(selected_components['area_work'])}` of floor-level work and `{fmt_m(shared_share)}` of shared building-wide cost.")
        )

        floor_table = floors_df.rename(
            columns={
                "floor": "Floor",
                "use": "Use",
                "included": "Included",
                "area": "Area (m2)",
                "light_total": "Light total",
                "mid_total": "Mid total",
                "heavy_total": "Heavy total",
            }
        ).copy()
        for column in ["Area (m2)", "Light total", "Mid total", "Heavy total"]:
            floor_table[column] = floor_table[column].map(lambda value: round(float(value), 1) if column == "Area (m2)" else nok(float(value)))
        st.dataframe(floor_table, use_container_width=True, hide_index=True)

        ctx["selected_renovation_total"] = selected_renovation_total
        ctx["selected_renovation_components"] = selected_components
        ctx["renovation_funding_needed"] = renovation_funding_needed
