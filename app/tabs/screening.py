from __future__ import annotations

import streamlit as st

from app.formatting import clamp_index, nok, risk_label, weighted_average


STATUS_SEVERITY = {
    "Confirmed": 0,
    "Likely but not confirmed": 1,
    "Unclear": 2,
    "Major risk": 3,
}

STATUS_SCORE = {
    "Confirmed": 90,
    "Likely but not confirmed": 65,
    "Unclear": 35,
    "Major risk": 10,
}


def render_screening_tab(tab, ctx: dict, default, label) -> None:
    with tab:
        status_options = ["Confirmed", "Likely but not confirmed", "Unclear", "Major risk"]
        st.subheader(label("screening.title", "Screening and diligence framework"))
        st.caption(
            label("screening.caption_1", f"Use this as the front door for `{ctx['candidate_building_name']}`: record what is actually confirmed, then score the remaining assumptions.")
        )
        st.caption(label("screening.caption_2", "Sidebar inputs already hold price, financing, floors, and ministry baseline. This tab is for gateway judgment, diligence status, and fit."))

        pbe_use_status = st.session_state.get("screening_pbe_use_status", "Unclear")
        pbe_fire_status = st.session_state.get("screening_pbe_fire_status", "Unclear")
        pbe_vent_status = st.session_state.get("screening_pbe_vent_status", "Unclear")
        pbe_access_status = st.session_state.get("screening_pbe_access_status", "Unclear")

        st.markdown(f"### 1. {label('screening.sections.confirmed_facts', 'Confirmed diligence facts')}")
        st.caption(label("screening.confirmed_facts_caption", "Use these fields for facts you believe are actually checked. These statuses override weaker heuristic slider values in the summary below."))
        pbe_use_status = st.selectbox("Confidence on permitted church / assembly use", status_options, index=clamp_index(status_options.index(pbe_use_status), len(status_options)), key="screening_pbe_use_status", help="Use this to record your current PBE or legal-use confidence: confirmed, likely, unclear, or a major deal risk.")
        pbe_fire_status = st.selectbox("Confidence on fire / egress compliance", status_options, index=clamp_index(status_options.index(pbe_fire_status), len(status_options)), key="screening_pbe_fire_status", help="Use this to record how confident you are that fire alarm, egress, occupancy, and related life-safety requirements are manageable.")
        pbe_vent_status = st.selectbox("Confidence on ventilation for assembly occupancy", status_options, index=clamp_index(status_options.index(pbe_vent_status), len(status_options)), key="screening_pbe_vent_status", help="Use this to record how confident you are that the building can satisfy ventilation expectations for worship and gathering use.")
        pbe_access_status = st.selectbox("Confidence on accessibility / universal design", status_options, index=clamp_index(status_options.index(pbe_access_status), len(status_options)), key="screening_pbe_access_status", help="Use this to record how confident you are that access, circulation, toilets, and level changes can meet practical and regulatory accessibility expectations.")
        parking_overflow = st.checkbox("Include gravel / overflow / nearby street support", value=True, help="Turn this on if the practical case includes extra informal or nearby parking beyond the core on-site count.")
        diligence_statuses = {
            "Use / zoning": pbe_use_status,
            "Fire / egress": pbe_fire_status,
            "Ventilation": pbe_vent_status,
            "Accessibility": pbe_access_status,
        }
        unresolved_sorted = sorted(
            diligence_statuses.items(),
            key=lambda item: (STATUS_SEVERITY[item[1]], item[0]),
            reverse=True,
        )
        largest_unresolved_area, largest_unresolved_status = unresolved_sorted[0]
        confirmed_core_checks = sum(1 for status in diligence_statuses.values() if status == "Confirmed")
        if largest_unresolved_status == "Confirmed":
            largest_unresolved_text = "No major unresolved diligence area"
            largest_unresolved_delta = "all core checks confirmed"
        else:
            largest_unresolved_text = largest_unresolved_area
            largest_unresolved_delta = largest_unresolved_status

        st.markdown(f"### 2. {label('screening.sections.assumptions', 'Screening assumptions')}")
        st.caption(label("screening.assumptions_caption", "These are directional judgments where you may not have hard confirmation yet."))
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

        effective_zoning_score = max(zoning_confidence, STATUS_SCORE[pbe_use_status])
        effective_fire_score = max(fire_score, STATUS_SCORE[pbe_fire_status])
        effective_ventilation_score = max(ventilation_score, STATUS_SCORE[pbe_vent_status])
        effective_accessibility_score = max(accessibility_score, STATUS_SCORE[pbe_access_status])

        building_readiness = weighted_average(
            [
                (electrical_score, 0.18),
                (effective_ventilation_score, 0.20),
                (effective_fire_score, 0.20),
                (structural_score, 0.18),
                (effective_accessibility_score, 0.12),
                (sound_score, 0.12),
            ]
        )
        site_fit = weighted_average([(min(screening_parking_spaces * 3, 100), 0.4), (transport_score, 0.35), (accessibility_score, 0.25)])
        regulatory_fit = weighted_average([(effective_zoning_score, 0.6), (effective_fire_score, 0.2), (lease_income_visibility, 0.2)])

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
        if STATUS_SEVERITY[pbe_use_status] >= STATUS_SEVERITY["Unclear"] or effective_zoning_score < 45:
            red_flags.append("Permitted-use confidence is still weak")
        if STATUS_SEVERITY[pbe_fire_status] >= STATUS_SEVERITY["Unclear"] or effective_fire_score < 45:
            red_flags.append("Fire / egress readiness looks fragile")
        if STATUS_SEVERITY[pbe_vent_status] >= STATUS_SEVERITY["Unclear"] or effective_ventilation_score < 45:
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
        biggest_legal_blocker = "Use permission / PBE confidence is still too low" if STATUS_SEVERITY[pbe_use_status] >= STATUS_SEVERITY["Unclear"] or effective_zoning_score < 50 else "No major legal blocker visible yet"
        biggest_cost_blocker = "Ventilation / fire / hidden systems may create a heavy renovation burden" if max(STATUS_SEVERITY[pbe_fire_status], STATUS_SEVERITY[pbe_vent_status]) >= STATUS_SEVERITY["Unclear"] or min(effective_ventilation_score, effective_fire_score, structural_score) < 50 else "No dominant cost blocker visible yet"
        biggest_fit_blocker = "Main hall and support-room fit may be tight for intended ministry use" if hall_fit_score < 55 else "No dominant fit blocker visible yet"
        positive_case = []
        if site_fit >= 60:
            positive_case.append("location and access are workable")
        if building_readiness >= 55:
            positive_case.append("the base building does not look hopeless")
        if lease_income_visibility >= 50:
            positive_case.append("income support is at least partly evidenced")
        positive_case_text = ", ".join(positive_case[:3]) if positive_case else "the building still needs stronger positives before deeper work"

        st.markdown(f"### 3. {label('screening.sections.gateway_summary', 'Gateway summary')}")
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
        q1, q2, q3 = st.columns(3)
        parking_status = "Assumed strong" if screening_parking_spaces >= 40 else "Usable but tighter" if screening_parking_spaces >= 25 else "Potential constraint"
        q1.metric("Core checks confirmed", f"{confirmed_core_checks}/4")
        q2.metric("Largest unresolved area", largest_unresolved_text, largest_unresolved_delta)
        q3.metric("Parking assumption", f"{screening_parking_spaces}+ cars" if parking_overflow else f"{screening_parking_spaces} cars", parking_status)
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Building readiness", f"{building_readiness:.0f}/100")
        s2.metric("Location / access fit", f"{site_fit:.0f}/100")
        s3.metric("Approval / evidence fit", f"{regulatory_fit:.0f}/100")
        s4.metric("Financing fit", f"{finance_fit:.0f}/100")
        d1, d2, d3 = st.columns(3)
        d1.metric("Biggest legal blocker", biggest_legal_blocker)
        d2.metric("Biggest cost blocker", biggest_cost_blocker)
        d3.metric("Biggest fit blocker", biggest_fit_blocker)
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

        st.markdown(f"### 4. {label('screening.sections.financial_snapshot', 'Financial risk snapshot')}")
        st.caption(label("screening.financial_snapshot_caption", "This keeps the non-technical project risks visible in the same gateway tab: funding pressure, lease dependence, contingency strength, and execution complexity."))
        gap_ratio = max(ctx["funding_gap"], 0) / ctx["acquisition_cost"] if ctx["acquisition_cost"] else 0.0
        leverage_ratio = ctx["loan_used"] / ctx["acquisition_cost"] if ctx["acquisition_cost"] else 0.0
        current_income_coverage = ctx["annual_member_cashflow"] / ctx["debt_service"] if ctx["debt_service"] else 0.0
        finance_col1, finance_col2 = st.columns(2)
        with finance_col1:
            lease_lock_in = st.slider(
                "Lease lock-in pressure",
                0,
                100,
                default("risk", "lease_lock_in", 70),
                help="How much current leases restrict timing, space handback, or repurposing flexibility. Higher values mean less freedom to implement the floor plan quickly.",
            )
            income_dependency = st.slider(
                "Dependence on rental income",
                0,
                100,
                default("risk", "income_dependency", 60),
                help="How much the case depends on retained rent or shared-use income. Higher values mean the project weakens more if that income slips.",
            )
            management_complexity = st.slider(
                "Management / transition complexity",
                0,
                100,
                default("risk", "management_complexity", 55),
                help="How demanding the move, tenant handling, transition, and change execution feel. Higher values mean more delivery risk.",
            )
        with finance_col2:
            financing_pressure = st.slider(
                "Financing pressure",
                0,
                100,
                default("risk", "financing_pressure", 75),
                help="How tight the financing picture feels. Higher values mean less room for surprises in bid, timing, renovation, or overlap cost.",
            )
            market_buffer = st.slider(
                "Market / value cushion",
                0,
                100,
                default("risk", "market_buffer", 40),
                help="How much price cushion you believe exists relative to market value and fallback saleability. Higher values improve resilience.",
            )
            contingency_cover = st.slider(
                "Contingency strength",
                0,
                100,
                default("risk", "contingency_cover", 45),
                help="How strong your fallback reserves, contingency allowances, and backup plans are. Higher values reduce effective project risk.",
            )

        financing_score = min(100.0, financing_pressure * 0.6 + gap_ratio * 200 + leverage_ratio * 25)
        resilience_penalty = 100 - contingency_cover
        cushion_penalty = 100 - market_buffer
        financial_risk = weighted_average(
            [
                (financing_score, 0.38),
                (lease_lock_in, 0.18),
                (income_dependency, 0.18),
                (management_complexity, 0.14),
                (resilience_penalty, 0.08),
                (cushion_penalty, 0.04),
            ]
        )

        f1, f2, f3, f4 = st.columns(4)
        f1.metric("Financial risk score", f"{financial_risk:.0f}/100", risk_label(financial_risk))
        f2.metric("Current funding gap", nok(ctx["funding_gap"]))
        f3.metric("Loan as % of acquisition", f"{leverage_ratio * 100:.0f}%")
        f4.metric("Free-cash coverage of debt", f"{current_income_coverage:.2f}x")
        if ctx["funding_gap"] > 0:
            st.error(f"Current funding gap at this bid: {nok(ctx['funding_gap'])}")
        else:
            st.success(f"Cash left after acquisition: {nok(max(ctx['cash_left_after_acquisition'], 0.0))}")
        st.caption(
            f"Decision-maker reading: the current financing case looks `{risk_label(financial_risk).lower()}` from a financial-risk perspective, with `{nok(ctx['funding_gap'])}` funding gap and `{current_income_coverage:.2f}x` free-cash coverage of annual debt service before property income."
        )

        st.markdown(f"### 5. {label('screening.sections.checklist', 'Diligence checklist')}")
        st.caption(label("screening.checklist_caption", "This is the working checklist behind the summary above. Use it to keep unknowns explicit and assign the next concrete verification task."))
        st.table(
            [
                {"Factor": "PBE / zoning / lawful assembly use", "Current status": pbe_use_status, "What we have": "Use this row to capture whether church / assembly use is formally confirmed, likely, unclear, or a major risk.", "Why it matters": "Could block or materially condition the intended worship and weekday-use model.", "Next check": "Get planning / zoning confirmation, current regulated use, and whether change-of-use approval is required."},
                {"Factor": "Fire strategy / sprinkler requirement", "Current status": pbe_fire_status, "What we have": "Modeled only as risk and cost allowance.", "Why it matters": "Could materially change capex and allowed occupancy.", "Next check": "Fire consultant review for intended assembly occupancy and phased use."},
                {"Factor": "Ventilation capacity for assembly use", "Current status": pbe_vent_status, "What we have": "Recognized in planning notes and renovation allowance.", "Why it matters": "Large gatherings may require major HVAC upgrade.", "Next check": "Mechanical review against target hall occupancy."},
                {"Factor": "Accessibility / universal design", "Current status": pbe_access_status, "What we have": "Captured as a property-fit score and possible renovation scope, but not confirmed against regulatory expectations.", "Why it matters": "May affect lawful use, inclusiveness, and renovation scope.", "Next check": "Check entrance, circulation, toilets, and level changes against intended occupancy and municipality expectations."},
                {"Factor": "Kitchen legality / suitability", "Current status": "Partly evidenced", "What we have": "Sales material and planning notes mention kitchen/support areas.", "Why it matters": "Existing kitchen presence is not the same as permitted intended use.", "Next check": "Confirm approvals, grease extraction, hygiene, and intended operating mode."},
                {"Factor": "Parking capacity", "Current status": "Assumed strong", "What we have": f"Working assumption: about {screening_parking_spaces}+ cars" if parking_overflow else f"Working assumption: about {screening_parking_spaces} cars", "Why it matters": "Important for Sunday gatherings and weekday use.", "Next check": "Confirm official marked/approved spaces and any access constraints."},
                {"Factor": "Current tenants / rental income", "Current status": "Reviewed but must be re-confirmed", "What we have": "Lease summary indicates visible tenants and active lease timing.", "Why it matters": "Drives both income support and space lock-in.", "Next check": "Confirm tenant status on closing date and any exercised options."},
                {"Factor": "Technical condition: roof / drainage / electrical", "Current status": "Unknown", "What we have": "No technical-condition survey in repo.", "Why it matters": "Could create immediate hidden capex beyond renovation model.", "Next check": "Commission technical due diligence with priority on roof, water ingress, drainage, electrical, and core systems."},
                {"Factor": "Operating costs on a large building", "Current status": "Modeled, not audited", "What we have": "Detailed side-by-side operating model in app.", "Why it matters": "A large building can become cash-flow heavy even if purchase price looks manageable.", "Next check": "Benchmark utilities, insurance, maintenance, and caretaker cost against actual history."},
            ]
        )
        if all(status == "Confirmed" for status in diligence_statuses.values()):
            st.success("Current honest position: the core PBE, fire, ventilation, and accessibility checks are marked confirmed. Remaining work is mainly normal technical, tenancy, and operating-cost verification.")
        elif any(status == "Major risk" for status in diligence_statuses.values()):
            st.error("Current honest position: at least one core diligence area is still marked as a major risk. Do not treat the case as de-risked until that item is resolved.")
        elif any(status == "Unclear" for status in diligence_statuses.values()):
            st.warning("Current honest position: financing and directional economics can be scaffolded early, but at least one core diligence area is still unclear.")
        else:
            st.info("Current honest position: the core diligence picture is improving, but some items are still likely rather than fully confirmed.")

        ctx["screening_proceed_signal"] = proceed_signal
        ctx["screening_score"] = screening_score
        ctx["screening_red_flags"] = red_flags
        ctx["screening_confirmed_core_checks"] = confirmed_core_checks
        ctx["screening_largest_unresolved_area"] = largest_unresolved_text
        ctx["screening_largest_unresolved_status"] = largest_unresolved_delta
        ctx["screening_financial_risk"] = financial_risk
        ctx["screening_financing_fit"] = finance_fit
