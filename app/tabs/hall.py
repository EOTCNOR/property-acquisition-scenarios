from __future__ import annotations

import pandas as pd
import streamlit as st

from app.formatting import nok


def render_hall_tab(tab, ctx: dict, default, label) -> None:
    with tab:
        st.subheader(label("space.title", "Space utilization"))
        st.caption(
            label("space.caption", "This is the floor-by-floor planning base for the rest of the tool. Define what each floor is for here, then use the same floor logic in Renovation Cost and Income Generation.")
        )

        assembly_floor_number = st.selectbox(
            "Main assembly hall floor",
            list(range(1, ctx["candidate_floors"] + 1)),
            index=0,
            key="space_assembly_floor",
            help="Select which floor contains the main worship / assembly hall. That floor will drive the hall and tabot capacity calculation.",
        )

        density_col1, density_col2 = st.columns(2)
        with density_col1:
            dense_space_per_person = st.slider(
                "Dense seating m2 per person",
                0.5,
                1.5,
                default("hall", "min_space_per_person", 0.8),
                0.05,
                key="space_dense_m2_per_person",
                help="Area allowed per person in a dense layout. Lower values increase capacity but may be less realistic or less comfortable.",
            )
        with density_col2:
            comfort_space_per_person = st.slider(
                "Comfortable seating m2 per person",
                0.5,
                2.0,
                default("hall", "max_space_per_person", 1.0),
                0.05,
                key="space_comfort_m2_per_person",
                help="Area allowed per person in a more comfortable layout. Higher values reduce capacity but improve circulation and comfort.",
            )

        total_support_rooms = 0
        total_support_room_seats = 0
        total_possible_rental_income = 0.0
        assembly_gross_area = 0.0
        floor_summary_rows: list[dict[str, float | int | str]] = []

        for floor_no in range(1, ctx["candidate_floors"] + 1):
            floor_label = f"Floor {floor_no}"
            with st.expander(floor_label, expanded=floor_no == assembly_floor_number):
                width_col, length_col = st.columns(2)
                with width_col:
                    floor_width = st.number_input(
                        f"{floor_label} width (m)",
                        min_value=0.0,
                        value=float(st.session_state.get(f"space_floor_width_{floor_no}", 19.0)),
                        step=0.5,
                        key=f"space_floor_width_{floor_no}",
                        help="Measured usable internal width for this floor's main zone.",
                    )
                with length_col:
                    floor_length = st.number_input(
                        f"{floor_label} length (m)",
                        min_value=0.0,
                        value=float(st.session_state.get(f"space_floor_length_{floor_no}", 20.0)),
                        step=0.5,
                        key=f"space_floor_length_{floor_no}",
                        help="Measured usable internal length for this floor's main zone.",
                    )
                floor_area = floor_width * floor_length
                st.caption(f"{floor_label} gross area from measurements: `{floor_area:,.0f} m2`")

                if floor_no == assembly_floor_number:
                    assembly_gross_area = floor_area
                    tabot_col1, tabot_col2 = st.columns(2)
                    with tabot_col1:
                        tabot_width = st.number_input(
                            "Tabot / sacred area width (m)",
                            min_value=0.0,
                            value=float(st.session_state.get("space_tabot_width", 4.0)),
                            step=0.5,
                            key="space_tabot_width",
                            help="Measured width of the sacred / tabot zone to exclude from seating capacity.",
                        )
                    with tabot_col2:
                        tabot_length = st.number_input(
                            "Tabot / sacred area length (m)",
                            min_value=0.0,
                            value=float(st.session_state.get("space_tabot_length", 20.0)),
                            step=0.5,
                            key="space_tabot_length",
                            help="Measured length of the sacred / tabot zone to exclude from seating capacity.",
                        )
                    tabot_area = tabot_width * tabot_length
                    seating_area = max(floor_area - tabot_area, 0.0)
                    likely_capacity = int(seating_area / comfort_space_per_person) if comfort_space_per_person else 0
                    upper_capacity = int(seating_area / dense_space_per_person) if dense_space_per_person else 0
                    a1, a2, a3, a4 = st.columns(4)
                    a1.metric("Gross hall area", f"{floor_area:,.0f} m2")
                    a2.metric("Tabot / sacred area", f"{tabot_area:,.0f} m2")
                    a3.metric("Likely hall capacity", f"{likely_capacity}")
                    a4.metric("Upper hall capacity", f"{upper_capacity}")
                    st.caption("Seating area is calculated as measured hall area minus the measured tabot / sacred area.")
                    floor_summary_rows.append(
                        {
                            "Floor": floor_label,
                            "Planned use": "Assembly hall",
                            "Area (m2)": floor_area,
                            "Rooms": 0,
                            "Room seats": 0,
                            "Rental seed": 0.0,
                        }
                    )
                else:
                    floor_use = st.selectbox(
                        f"{floor_label} primary use",
                        ["Support rooms", "Dining / common", "Rental", "Mixed / other", "Unused / circulation"],
                        index=0,
                        key=f"space_floor_use_{floor_no}",
                        help="Choose how this floor is mainly expected to be used in the working scenario.",
                    )
                    if floor_use in {"Support rooms", "Mixed / other"}:
                        room_col1, room_col2 = st.columns(2)
                        with room_col1:
                            floor_rooms = st.number_input(
                                f"{floor_label} usable rooms",
                                min_value=0,
                                value=int(st.session_state.get(f"space_floor_rooms_{floor_no}", 4)),
                                step=1,
                                key=f"space_floor_rooms_{floor_no}",
                                help="Approximate number of usable classrooms, meeting rooms, offices, or counseling rooms on this floor.",
                            )
                        with room_col2:
                            floor_room_capacity = st.number_input(
                                f"{floor_label} average people per room",
                                min_value=0,
                                value=int(st.session_state.get(f"space_floor_room_capacity_{floor_no}", 12)),
                                step=1,
                                key=f"space_floor_room_capacity_{floor_no}",
                                help="Average number of people each usable room on this floor can accommodate.",
                            )
                        total_support_rooms += floor_rooms
                        total_support_room_seats += floor_rooms * floor_room_capacity
                    if floor_use in {"Rental", "Mixed / other"}:
                        possible_rental_income = st.number_input(
                            f"{floor_label} possible annual rental income",
                            min_value=0,
                            value=int(st.session_state.get(f"space_floor_rental_income_{floor_no}", 0)),
                            step=25_000,
                            key=f"space_floor_rental_income_{floor_no}",
                            help="Estimated annual income if this floor or part of it is retained as rental space.",
                        )
                        total_possible_rental_income += possible_rental_income
                    if floor_use == "Dining / common":
                        dining_capacity = st.number_input(
                            f"{floor_label} dining / common-use capacity",
                            min_value=0,
                            value=int(st.session_state.get(f"space_floor_common_capacity_{floor_no}", 80)),
                            step=5,
                            key=f"space_floor_common_capacity_{floor_no}",
                            help="Approximate number of people this floor can support in dining, gathering, or common-use mode.",
                        )
                        st.caption(f"Working common-area capacity on {floor_label}: `{dining_capacity}` people")
                    floor_summary_rows.append(
                        {
                            "Floor": floor_label,
                            "Planned use": floor_use,
                            "Area (m2)": floor_area,
                            "Rooms": int(st.session_state.get(f"space_floor_rooms_{floor_no}", 0)) if floor_use in {"Support rooms", "Mixed / other"} else 0,
                            "Room seats": (
                                int(st.session_state.get(f"space_floor_rooms_{floor_no}", 0))
                                * int(st.session_state.get(f"space_floor_room_capacity_{floor_no}", 12))
                                if floor_use in {"Support rooms", "Mixed / other"}
                                else 0
                            ),
                            "Rental seed": float(st.session_state.get(f"space_floor_rental_income_{floor_no}", 0.0)) if floor_use in {"Rental", "Mixed / other"} else 0.0,
                        }
                    )

        effective_tabot_area = float(st.session_state.get("space_tabot_width", 4.0)) * float(st.session_state.get("space_tabot_length", 20.0))
        effective_seating_area = max(assembly_gross_area - effective_tabot_area, 0.0)
        likely_capacity = int(effective_seating_area / comfort_space_per_person) if comfort_space_per_person else 0
        upper_capacity = int(effective_seating_area / dense_space_per_person) if dense_space_per_person else 0

        st.markdown(f"### {label('space.sections.planning_summary', 'Planning summary')}")
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Assembly gross area", f"{assembly_gross_area:,.0f} m2")
        s2.metric("Tabot / sacred area", f"{effective_tabot_area:,.0f} m2")
        s3.metric("Likely hall capacity", f"{likely_capacity}")
        s4.metric("Upper hall capacity", f"{upper_capacity}")

        r1, r2, r3 = st.columns(3)
        r1.metric("Support rooms", f"{total_support_rooms}")
        r2.metric("Support-room seats", f"{total_support_room_seats}")
        r3.metric("Possible rental income", nok(total_possible_rental_income))

        st.caption(label("space.summary_caption", "Decision-maker reading: this tab defines the intended role of each floor. The same floor plan should be visible again in renovation scope and income assumptions."))

        floor_summary_df = pd.DataFrame(floor_summary_rows)
        if not floor_summary_df.empty:
            floor_summary_df["Area (m2)"] = floor_summary_df["Area (m2)"].map(lambda value: round(float(value), 1))
            floor_summary_df["Rental seed"] = floor_summary_df["Rental seed"].map(lambda value: nok(float(value)))
            st.dataframe(floor_summary_df, use_container_width=True, hide_index=True)

        ctx["space_assembly_floor"] = assembly_floor_number
        ctx["space_total_support_rooms"] = total_support_rooms
        ctx["space_total_support_room_seats"] = total_support_room_seats
        ctx["space_total_possible_rental_income"] = total_possible_rental_income
        ctx["space_assembly_gross_area"] = assembly_gross_area
        ctx["space_effective_tabot_area"] = effective_tabot_area
        ctx["space_likely_capacity"] = likely_capacity
        ctx["space_upper_capacity"] = upper_capacity
