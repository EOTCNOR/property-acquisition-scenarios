from __future__ import annotations

import streamlit as st

from app.formatting import clamp_index, nok, weighted_average


def render_screening_tab(tab, ctx: dict, default) -> None:
    with tab:
        st.subheader("Property screening framework")
        st.caption(
            f"Use this first tab as the repeatable front door for any deal. It helps {ctx['organization_name']} test whether `{ctx['candidate_building_name']}` deserves deeper diligence versus staying in `{ctx['current_building_name']}`."
        )
        st.caption("Core facts such as asking price, floors, area, financing, and ministry baseline already live in the sidebar. This tab should stay focused on screening judgment.")

        col1, col2 = st.columns(2)
        with col1:
            st.table(
                [
                    {"Focus area": "Main hall fit", "Key question": "Can the main worship hall comfortably carry the intended attendance after sacred/front/service areas are deducted?"},
                    {"Focus area": "Room support", "Key question": "Are there enough side rooms for classrooms, choir, counseling, kitchen support, admin, and youth use?"},
                    {"Focus area": "System burden", "Key question": "Which heavy-cost items are likely: electrical, ventilation, fire, plumbing/drainage, roof, facade, accessibility?"},
                ]
            )
        with col2:
            screening_parking_spaces = st.number_input("Parking spaces", min_value=0, value=int(default("profile", "candidate_parking_spaces", 25)), step=1, help="Working assumption for how many usable parking spaces the candidate property can realistically support for church and weekday use.")
            transport_score = st.slider("Public transport strength", 0, 100, int(default("profile", "public_transport_score", 70)), help="Score how easy it is to reach the building by bus, train, tram, or other public transport. Higher values mean stronger access without relying on cars.")
            accessibility_score = st.slider("Accessibility / barrier-free access", 0, 100, int(default("profile", "accessibility_score", 55)), help="Score how usable the building is for people with reduced mobility, including entrances, circulation, toilets, and vertical access.")
        z1, z2, z3 = st.columns(3)
        with z1:
            zoning_confidence = st.slider("Zoning / permitted-use confidence", 0, 100, int(default("profile", "zoning_confidence", 40)), help="Score how confident you are that the intended church and assembly use is legally possible without major approval risk.")
        with z2:
            sound_score = st.slider("Sound isolation / acoustic suitability", 0, 100, int(default("profile", "sound_score", 50)), help="Score whether the building is likely to work acoustically for worship, music, and gatherings without major sound-treatment burden or neighbor conflict.")
        with z3:
            lease_income_visibility = st.slider("Lease / income evidence quality", 0, 100, int(default("profile", "lease_income_visibility", 45)), help="Score how well the claimed rental income is evidenced by leases, rent schedules, payment history, and vacancy visibility.")

        b1, b2, b3, b4 = st.columns(4)
        with b1:
            electrical_score = st.slider("Electrical condition", 0, 100, int(default("profile", "electrical_score", 50)), help="Score the likely condition and adequacy of the electrical installation for church, office, kitchen, and event use.")
        with b2:
            ventilation_score = st.slider("Ventilation readiness", 0, 100, int(default("profile", "ventilation_score", 45)), help="Score how ready the building appears to be for assembly occupancy from a ventilation and indoor-air perspective.")
        with b3:
            fire_score = st.slider("Fire / egress readiness", 0, 100, int(default("profile", "fire_score", 40)), help="Score how likely it is that fire alarm, compartmentation, escape routes, occupancy, and related safety issues are manageable without major intervention.")
        with b4:
            structural_score = st.slider("Structure / hidden-work confidence", 0, 100, int(default("profile", "structural_score", 50)), help="Score your confidence that the building does not hide major structural, roof, drainage, or fabric issues that would materially change the project.")

        building_readiness = weighted_average([(electrical_score, 0.18), (ventilation_score, 0.20), (fire_score, 0.20), (structural_score, 0.18), (accessibility_score, 0.12), (sound_score, 0.12)])
        site_fit = weighted_average([(min(screening_parking_spaces * 3, 100), 0.4), (transport_score, 0.35), (accessibility_score, 0.25)])
        regulatory_fit = weighted_average([(zoning_confidence, 0.6), (fire_score, 0.2), (lease_income_visibility, 0.2)])

        s1, s2, s3 = st.columns(3)
        s1.metric("How ready the building is", f"{building_readiness:.0f}/100")
        s2.metric("Location / access fit", f"{site_fit:.0f}/100")
        s3.metric("Approval and evidence confidence", f"{regulatory_fit:.0f}/100")

        assembly_floor_number = int(st.session_state.get("space_assembly_floor", 1))
        assembly_floor_width = float(st.session_state.get(f"space_floor_width_{assembly_floor_number}", 19.0))
        assembly_floor_length = float(st.session_state.get(f"space_floor_length_{assembly_floor_number}", 20.0))
        dense = float(st.session_state.get("space_dense_m2_per_person", default("hall", "min_space_per_person", 0.8)))
        comfort = float(st.session_state.get("space_comfort_m2_per_person", default("hall", "max_space_per_person", 1.0)))
        sacred_area = float(st.session_state.get("space_tabot_width", 4.0)) * float(st.session_state.get("space_tabot_length", 20.0))
        gross_hall = assembly_floor_width * assembly_floor_length
        hall_fit_area = max(gross_hall - sacred_area, 0.0)
        support_rooms = 0
        support_room_seats = 0
        possible_rental_income = 0.0
        for floor_no in range(1, ctx["candidate_floors"] + 1):
            floor_use = st.session_state.get(f"space_floor_use_{floor_no}", "Support rooms")
            floor_room_count = int(st.session_state.get(f"space_floor_rooms_{floor_no}", 0))
            floor_room_capacity = int(st.session_state.get(f"space_floor_room_capacity_{floor_no}", 12))
            floor_rental_income = float(st.session_state.get(f"space_floor_rental_income_{floor_no}", 0.0))
            if floor_no != assembly_floor_number and floor_use in {"Support rooms", "Mixed / other"}:
                support_rooms += floor_room_count
                support_room_seats += floor_room_count * floor_room_capacity
            if floor_no != assembly_floor_number and floor_use in {"Rental", "Mixed / other"}:
                possible_rental_income += floor_rental_income

        likely_capacity = int(hall_fit_area / comfort) if comfort else 0
        upper_capacity = int(hall_fit_area / dense) if dense else 0
        hall_fit_score = min(100.0, weighted_average([(min(likely_capacity / 4, 100), 0.55), (min(support_room_seats * 2, 100), 0.25), (sound_score, 0.20)]))
        finance_fit = weighted_average(
            [
                (max(0.0, 100 - min((ctx["debt_service"] / max(ctx["annual_member_cashflow"], 1.0)) * 100, 150)), 0.45),
                (max(0.0, 100 - min((max(ctx["funding_gap"], 0.0) / max(ctx["acquisition_cost"], 1.0)) * 200, 100)), 0.35),
                (max(0.0, 100 - min((ctx["loan_used"] / max(ctx["acquisition_cost"], 1.0)) * 100, 100)), 0.20),
            ]
        )
        screening_score = weighted_average([(building_readiness, 0.25), (site_fit, 0.15), (regulatory_fit, 0.25), (hall_fit_score, 0.20), (finance_fit, 0.15)])
        red_flags: list[str] = []
        if zoning_confidence < 45:
            red_flags.append("Permitted-use confidence is still weak")
        if fire_score < 45:
            red_flags.append("Fire / egress readiness looks fragile")
        if ventilation_score < 45:
            red_flags.append("Ventilation for assembly use may need major work")
        if likely_capacity < 250:
            red_flags.append("Hall capacity may be tight for major worship use")
        if finance_fit < 45 or ctx["annual_member_cashflow"] < ctx["debt_service"]:
            red_flags.append("Financing support looks thin relative to mortgage burden")

        proceed_signal = "Proceed" if screening_score >= 68 and len(red_flags) <= 1 else "Proceed With Conditions" if screening_score >= 50 else "Do Not Proceed Yet"
        proceed_note = (
            "This building looks strong enough to justify deeper diligence."
            if proceed_signal == "Proceed"
            else "There is a plausible case here, but only if the blockers below are addressed early."
            if proceed_signal == "Proceed With Conditions"
            else "The case still looks too fragile at gateway level."
        )
        biggest_legal_blocker = "Use permission / PBE confidence is still too low" if zoning_confidence < 50 else "No major legal blocker visible yet"
        biggest_cost_blocker = "Ventilation / fire / hidden systems may create a heavy renovation burden" if min(ventilation_score, fire_score, structural_score) < 50 else "No dominant cost blocker visible yet"
        biggest_fit_blocker = "Main hall and support-room fit may be tight for intended ministry use" if hall_fit_score < 55 else "No dominant fit blocker visible yet"
        positive_case = []
        if site_fit >= 60:
            positive_case.append("location and access are workable")
        if building_readiness >= 55:
            positive_case.append("the base building does not look hopeless")
        if lease_income_visibility >= 50:
            positive_case.append("income support is at least partly evidenced")
        positive_case_text = ", ".join(positive_case[:3]) if positive_case else "the building still needs stronger positives before deeper work"

        g1, g2, g3, g4 = st.columns(4)
        g1.metric("Proceed Signal", proceed_signal)
        g2.metric("Gateway score", f"{screening_score:.0f}/100")
        g3.metric("Red flags", f"{len(red_flags)}")
        g4.metric("Likely hall capacity", f"{likely_capacity}")
        if proceed_signal == "Proceed":
            st.success(proceed_note)
        elif proceed_signal == "Proceed With Conditions":
            st.warning(proceed_note)
        else:
            st.error(proceed_note)
        b1, b2, b3 = st.columns(3)
        b1.metric("Biggest legal blocker", biggest_legal_blocker)
        b2.metric("Biggest cost blocker", biggest_cost_blocker)
        b3.metric("Biggest fit blocker", biggest_fit_blocker)
        h1, h2, h3, h4 = st.columns(4)
        h1.metric("Upper hall capacity", f"{upper_capacity}")
        h2.metric("Support rooms", f"{support_rooms}")
        h3.metric("Support-room seats", f"{support_room_seats}")
        h4.metric("Hall-fit score", f"{hall_fit_score:.0f}/100")
        if possible_rental_income > 0:
            st.caption(f"Possible annual rental income from non-hall floors currently marked as rental or mixed: `{nok(possible_rental_income)}`.")
        if red_flags:
            st.markdown("**Key next checks before deeper work**")
            for item in red_flags[:3]:
                st.write(f"- {item}")
        st.caption(f"Why this might still work: {positive_case_text}.")
        st.table(
            [
                {"Category": "Building fabric and systems", "What to test": "Roof, drainage, structure, electrical, ventilation, heating, fire alarm, sprinkler, sound isolation, lift/accessibility.", "Why it matters": "This determines hidden capex and whether the building can realistically support worship, weekday use, and rentals."},
                {"Category": "Zoning and regulation", "What to test": "Lawful use, assembly permission, fire strategy, occupancy limits, kitchen rules, municipal conditions, heritage or neighbor restrictions.", "Why it matters": "A cheap building can still fail if the intended church use is delayed, capped, or blocked."},
                {"Category": "Access and location", "What to test": "Parking, disabled access, public transport, drop-off, road approach, winter access, neighborhood fit.", "Why it matters": "Sunday attendance and weekday ministry depend on people actually being able to reach and use the place."},
                {"Category": "Income support", "What to test": "Existing leases, lease expiry, notice rights, rent per year, vacancy upside, realistic collection quality, running cost burden.", "Why it matters": "Property income can materially reduce carrying cost, but only if it survives transition and is collectible."},
                {"Category": "Bankability", "What to test": "Loan size, interest rate, amortization years, covenant conditions, collateral release on sale, and yearly mortgage burden.", "Why it matters": "The church must survive the repayment profile, not just win the bid."},
                {"Category": "Overlap and ministry resilience", "What to test": f"How long {ctx['organization_name']} can carry both `{ctx['current_building_name']}` and `{ctx['candidate_building_name']}`, including overlap, moving, and ministry-running costs.", "Why it matters": "Many deals fail in the bridge period rather than in the final steady state."},
            ]
        )
