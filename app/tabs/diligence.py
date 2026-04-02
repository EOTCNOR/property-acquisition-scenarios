from __future__ import annotations

import streamlit as st


def render_diligence_tab(tab) -> None:
    with tab:
        st.subheader("PBE and due-diligence perspective")
        st.caption("This tab keeps PBE, code, and diligence unknowns visible. It is a sensitizing checklist, not a legal or technical conclusion.")
        pbe_use_status = st.selectbox("Confidence on permitted church / assembly use", ["Confirmed", "Likely but not confirmed", "Unclear", "Major risk"], index=2, help="Use this to record your current PBE or legal-use confidence: confirmed, likely, unclear, or a major deal risk.")
        pbe_fire_status = st.selectbox("Confidence on fire / egress compliance", ["Confirmed", "Likely but not confirmed", "Unclear", "Major risk"], index=2, help="Use this to record how confident you are that fire alarm, egress, occupancy, and related life-safety requirements are manageable.")
        pbe_vent_status = st.selectbox("Confidence on ventilation for assembly occupancy", ["Confirmed", "Likely but not confirmed", "Unclear", "Major risk"], index=2, help="Use this to record how confident you are that the building can satisfy ventilation expectations for worship and gathering use.")
        pbe_access_status = st.selectbox("Confidence on accessibility / universal design", ["Confirmed", "Likely but not confirmed", "Unclear", "Major risk"], index=2, help="Use this to record how confident you are that access, circulation, toilets, and level changes can meet practical and regulatory accessibility expectations.")
        parking_spaces = st.number_input("Working parking capacity assumption", min_value=0, value=40, step=1, help="Current planning assumption for on-site parking under church control. Your latest working assumption is about 40+ cars.")
        parking_overflow = st.checkbox("Include gravel / overflow / nearby street support", value=True, help="Turn this on if the practical case includes extra informal or nearby parking beyond the core on-site count.")
        parking_status = "Assumed strong" if parking_spaces >= 40 else "Usable but tighter" if parking_spaces >= 25 else "Potential constraint"
        d1, d2, d3 = st.columns(3)
        d1.metric("Parking assumption", f"{parking_spaces}+ cars" if parking_overflow else f"{parking_spaces} cars", parking_status)
        d2.metric("PBE use status", pbe_use_status, "manual screening state")
        d3.metric("Largest unresolved area", "Use / fire / technical", "confirm early")
        diligence_rows = [
            {"Factor": "PBE / zoning / lawful assembly use", "Current status": pbe_use_status, "What we have": "Use this row to capture whether church / assembly use is formally confirmed, likely, unclear, or a major risk.", "Why it matters": "Could block or materially condition the intended worship and weekday-use model.", "Next check": "Get planning / zoning confirmation, current regulated use, and whether change-of-use approval is required."},
            {"Factor": "Fire strategy / sprinkler requirement", "Current status": pbe_fire_status, "What we have": "Modeled only as risk and cost allowance.", "Why it matters": "Could materially change capex and allowed occupancy.", "Next check": "Fire consultant review for intended assembly occupancy and phased use."},
            {"Factor": "Ventilation capacity for assembly use", "Current status": pbe_vent_status, "What we have": "Recognized in planning notes and renovation allowance.", "Why it matters": "Large gatherings may require major HVAC upgrade.", "Next check": "Mechanical review against target hall occupancy."},
            {"Factor": "Accessibility / universal design", "Current status": pbe_access_status, "What we have": "Captured as a property-fit score and possible renovation scope, but not confirmed against regulatory expectations.", "Why it matters": "May affect lawful use, inclusiveness, and renovation scope.", "Next check": "Check entrance, circulation, toilets, and level changes against intended occupancy and municipality expectations."},
            {"Factor": "Kitchen legality / suitability", "Current status": "Partly evidenced", "What we have": "Sales material and planning notes mention kitchen/support areas.", "Why it matters": "Existing kitchen presence is not the same as permitted intended use.", "Next check": "Confirm approvals, grease extraction, hygiene, and intended operating mode."},
            {"Factor": "Parking capacity", "Current status": "Assumed strong", "What we have": f"Working assumption: about {parking_spaces}+ cars" if parking_overflow else f"Working assumption: about {parking_spaces} cars", "Why it matters": "Important for Sunday gatherings and weekday use.", "Next check": "Confirm official marked/approved spaces and any access constraints."},
            {"Factor": "Current tenants / rental income", "Current status": "Reviewed but must be re-confirmed", "What we have": "Lease summary indicates 5 visible tenants and active lease timing.", "Why it matters": "Drives both income support and space lock-in.", "Next check": "Confirm tenant status on closing date and any exercised options."},
            {"Factor": "Technical condition: roof / drainage / electrical", "Current status": "Unknown", "What we have": "No technical-condition survey in repo.", "Why it matters": "Could create immediate hidden capex beyond renovation model.", "Next check": "Commission technical due diligence with priority on roof, water ingress, drainage, electrical, and core systems."},
            {"Factor": "Operating costs on a large building", "Current status": "Modeled, not audited", "What we have": "Detailed side-by-side operating model in app.", "Why it matters": "A large building can become cash-flow heavy even if purchase price looks manageable.", "Next check": "Benchmark utilities, insurance, maintenance, and caretaker cost against actual history."},
        ]
        st.table(diligence_rows)
        st.warning("Current honest position: financing and directional economics can be scaffolded early, but PBE/use approval, fire, ventilation, and technical condition remain real diligence risks.")
