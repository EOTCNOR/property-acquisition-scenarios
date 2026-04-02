from __future__ import annotations

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from app.member_distribution import (
    CURRENT_CHURCH_COORDINATES,
    CURRENT_CHURCH_LABEL,
    SEARCH_AREA_COORDINATES,
    build_member_point_distribution,
    build_municipality_distribution,
    build_oslo_bydel_distribution,
    compare_reference_vs_candidates,
    build_fairness_shortlist,
    load_member_distribution,
    rank_search_areas,
    summarize_location,
    weighted_center,
)

try:
    import pydeck as pdk
except ImportError:  # pragma: no cover
    pdk = None


def _render_point_map(data: pd.DataFrame, label_column: str) -> None:
    map_data = data.dropna(subset=["lat", "lon"]).copy()
    if map_data.empty:
        st.info("Map view is not available for the current selection because there are no mapped coordinates.")
        return

    if "radius_metric" in map_data.columns:
        map_data["radius"] = map_data["radius_metric"].clip(lower=1) * 80
    else:
        map_data["radius"] = map_data["member_count"].clip(lower=1) * 80

    if "tooltip_label" not in map_data.columns:
        map_data["tooltip_label"] = (
            map_data[label_column].astype(str)
            + ": "
            + map_data["member_count"].astype(int).astype(str)
            + " members"
            + " ("
            + map_data["share_pct"].map(lambda value: f"{value:.1f}%")
            + ")"
        )

    if pdk is None:
        st.map(map_data.rename(columns={"lat": "latitude", "lon": "longitude"})[["latitude", "longitude"]])
        return

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_data,
        get_position="[lon, lat]",
        get_radius="radius",
        get_fill_color="[37, 99, 235, 160]",
        get_line_color="[30, 64, 175, 220]",
        line_width_min_pixels=1,
        pickable=True,
        stroked=True,
    )
    view_state = pdk.ViewState(
        latitude=float(map_data["lat"].mean()),
        longitude=float(map_data["lon"].mean()),
        zoom=8 if label_column == "bydel" else 6,
        pitch=0,
    )
    st.pydeck_chart(
        pdk.Deck(
            map_style=None,
            initial_view_state=view_state,
            layers=[layer],
            tooltip={"text": "{tooltip_label}"},
        ),
        use_container_width=True,
    )


def _render_sorted_bar_chart(data: pd.DataFrame, category_column: str, value_column: str, title: str) -> None:
    chart = (
        alt.Chart(data)
        .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
        .encode(
            x=alt.X(f"{value_column}:Q", title="Members"),
            y=alt.Y(
                f"{category_column}:N",
                sort=alt.SortField(field=value_column, order="descending"),
                title=None,
            ),
            tooltip=[
                alt.Tooltip(f"{category_column}:N", title=category_column.replace("_", " ").title()),
                alt.Tooltip(f"{value_column}:Q", title="Members", format=",.0f"),
            ],
        )
        .properties(height=max(280, len(data) * 22), title=title)
    )
    st.altair_chart(chart, use_container_width=True)


def render_member_geography_tab(tab, ctx: dict) -> None:
    with tab:
        st.subheader("Member geography")
        st.caption(
            "Use member postal-code distribution to see municipality-level concentration and an Oslo bydel estimate. This is intended for directional property search, not official district reporting."
        )

        df = load_member_distribution(str(Path(__file__).resolve().parents[2]))
        municipality = build_municipality_distribution(df)
        bydel, unmatched_oslo, unmatched_oslo_rows = build_oslo_bydel_distribution(df)
        member_points = build_member_point_distribution(df)
        center_lat, center_lon = weighted_center(member_points)

        total_rows = int(len(df))
        valid_rows = int(df["valid_row"].sum())
        missing_rows = total_rows - valid_rows
        oslo_rows = int(((df["valid_row"]) & (df["Kommunenavn"] == "OSLO")).sum())

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Member rows", f"{valid_rows}", help="Rows from the CSV with both postcode and municipality present. These are the rows used in the geography calculations.")
        m2.metric("Municipalities", f"{municipality['municipality'].nunique()}", help="Number of municipalities represented in the valid member rows.")
        m3.metric("Oslo rows", f"{oslo_rows}", help="Valid member rows whose municipality is OSLO. These rows feed the bydel estimate.")
        m4.metric("Rows skipped", f"{missing_rows}", help="Rows excluded because postcode or municipality is missing.")

        st.markdown("### Municipality distribution")
        top_n_municipalities = st.slider(
            "Municipalities to highlight",
            5,
            min(40, len(municipality)),
            min(15, len(municipality)),
            help="How many of the largest municipalities to show in the chart and top table.",
        )
        municipality_top = municipality.head(top_n_municipalities).copy()
        municipality_top["share_pct"] = municipality_top["share_pct"].round(1)
        municipality_table = municipality_top.rename(
            columns={
                "municipality": "Municipality",
                "member_count": "Members",
                "share_pct": "Share %",
            }
        )[["Municipality", "Members", "Share %"]]

        top_share = municipality_top["member_count"].sum() / valid_rows * 100 if valid_rows else 0.0
        st.caption(
            f"Top {top_n_municipalities} municipalities account for {top_share:.1f}% of valid member rows."
        )

        col1, col2 = st.columns([1.2, 1])
        with col1:
            _render_sorted_bar_chart(municipality_top, "municipality", "member_count", "Top municipalities by members")
        with col2:
            st.dataframe(municipality_table, use_container_width=True, hide_index=True)

        with st.expander("Full municipality table"):
            full_municipality_table = municipality.rename(
                columns={
                    "municipality": "Municipality",
                    "member_count": "Members",
                    "share_pct": "Share %",
                }
            )[["Municipality", "Members", "Share %"]].copy()
            full_municipality_table["Share %"] = full_municipality_table["Share %"].round(1)
            st.dataframe(full_municipality_table, use_container_width=True, hide_index=True)

        municipality_mapped = municipality_top.dropna(subset=["lat", "lon"])
        if not municipality_mapped.empty:
            st.caption(
                f"Municipality map currently covers {len(municipality_mapped)}/{len(municipality_top)} highlighted municipalities with coordinate lookups."
            )
        _render_point_map(municipality_mapped, "municipality")

        st.markdown("### Oslo bydel estimate")
        st.caption(
            "Bydel is estimated from Oslo postal codes. It is suitable for directional search planning but should not be treated as an official district registry."
        )

        if bydel.empty:
            st.info("No Oslo rows could be mapped to bydel from the current file.")
            return

        bydel["share_pct"] = bydel["share_pct"].round(1)
        bydel_table = bydel.rename(
            columns={
                "bydel": "Bydel",
                "member_count": "Members",
                "share_pct": "Share of matched Oslo (%)",
                "share_of_all_valid_pct": "Share of all valid members (%)",
            }
        )[["Bydel", "Members", "Share of matched Oslo (%)", "Share of all valid members (%)"]]

        matched_oslo = int(bydel["member_count"].sum())
        b1, b2, b3 = st.columns(3)
        b1.metric("Oslo rows matched to bydel", f"{matched_oslo}", help="Number of Oslo member rows whose postcodes could be assigned to a bydel.")
        b2.metric("Oslo rows unmatched", f"{unmatched_oslo}", help="Oslo rows that could not be assigned to a bydel from the current postcode mapping.")
        b3.metric("Matched share", f"{(matched_oslo / oslo_rows * 100) if oslo_rows else 0.0:.1f}%", help="Share of all valid Oslo rows that are covered by the current bydel mapping.")
        st.caption(
            "In the bydel table, `Share of matched Oslo (%)` uses only Oslo rows that could be mapped to a bydel. `Share of all valid members (%)` uses the full valid member base."
        )

        col1, col2 = st.columns([1.2, 1])
        with col1:
            _render_sorted_bar_chart(bydel, "bydel", "member_count", "Oslo bydeler by members")
        with col2:
            st.dataframe(bydel_table, use_container_width=True, hide_index=True)

        with st.expander("Full bydel table"):
            st.dataframe(bydel_table, use_container_width=True, hide_index=True)

        if unmatched_oslo > 0:
            with st.expander(f"Unmatched Oslo rows ({unmatched_oslo})"):
                st.dataframe(unmatched_oslo_rows, use_container_width=True, hide_index=True)

        _render_point_map(bydel, "bydel")

        st.markdown("### Search-area sweet spot")
        st.caption(
            "This ranking uses member-weighted geographic distance. Oslo members are represented by estimated bydel centers, and non-Oslo members by municipality centers."
        )
        st.caption(
            f"Estimated member center of gravity: `{center_lat:.4f}, {center_lon:.4f}`."
        )
        st.caption(
            "Weighted average distance means the average travel distance across the whole member base after weighting each member cluster by how many members it contains."
        )

        default_search_areas = ["Alna", "Furuset", "Grorud", "Stovner", "Helsfyr", "Bryn", "Økern", "Lørenskog", "Strømmen", "Ski"]
        selected_search_areas = st.multiselect(
            "Areas to compare for property search",
            options=list(SEARCH_AREA_COORDINATES.keys()),
            default=default_search_areas,
            help="Choose the areas you want to rank and compare as purchase-search zones.",
        )

        ranking = rank_search_areas(member_points, selected_search_areas)
        if ranking.empty:
            st.info("Select at least one search area to rank.")
            return

        best_area = ranking.iloc[0]
        current_church = summarize_location(
            member_points,
            CURRENT_CHURCH_COORDINATES[0],
            CURRENT_CHURCH_COORDINATES[1],
            CURRENT_CHURCH_LABEL,
        )
        r1, r2, r3 = st.columns(3)
        r1.metric("Best weighted fit", str(best_area["search_area"]), help="The selected search area with the lowest weighted average member distance.")
        r2.metric("Weighted average distance", f"{best_area['weighted_avg_distance_km']:.1f} km", help="Average distance across the whole member base after weighting each member cluster by its size. Lower is better for whole-network fairness.")
        r3.metric("Members within 10 km", f"{best_area['share_within_10km_pct']:.1f}%", help="Share of all valid members whose estimated distance to the selected location is 10 km or less.")

        st.markdown("#### Best fit vs current church")
        compare_rows = [
            {
                "Location": str(best_area["search_area"]),
                "Weighted avg distance (km)": round(float(best_area["weighted_avg_distance_km"]), 1),
                "Members within 10 km (%)": round(float(best_area["share_within_10km_pct"]), 1),
                "Members within 5 km (%)": round(float(best_area.get("share_within_5km_pct", 0.0)), 1),
                "Members within 20 km (%)": round(float(best_area["share_within_20km_pct"]), 1),
            },
            {
                "Location": CURRENT_CHURCH_LABEL,
                "Weighted avg distance (km)": round(float(current_church["weighted_avg_distance_km"]), 1),
                "Members within 10 km (%)": round(float(current_church["share_within_10km_pct"]), 1),
                "Members within 5 km (%)": round(float(current_church["share_within_5km_pct"]), 1),
                "Members within 20 km (%)": round(float(current_church["share_within_20km_pct"]), 1),
            },
        ]
        st.dataframe(pd.DataFrame(compare_rows), use_container_width=True, hide_index=True)
        st.caption(
            f"Compared with {CURRENT_CHURCH_LABEL}, `{best_area['search_area']}` changes weighted average distance by "
            f"{float(current_church['weighted_avg_distance_km']) - float(best_area['weighted_avg_distance_km']):.1f} km "
            f"and changes the share within 10 km by "
            f"{float(best_area['share_within_10km_pct']) - float(current_church['share_within_10km_pct']):.1f} percentage points."
        )

        st.markdown("#### Fairness-first shortlist")
        st.caption(
            "This shortlist favors locations that keep whole-network travel burden low while still improving practical reach. It penalizes locations that move weighted average distance above the current church."
        )
        st.caption(
            "Use this when your goal is fairness first: treat the whole member base evenly, while still preferring locations that improve practical access bands."
        )
        with st.expander("How the fairness-first shortlist is calculated"):
            st.markdown(
                """
                `Fairness-first shortlist` is a ranking built for the principle:
                treat the whole member base evenly, but still prefer locations that improve practical access.

                `Fairness-first score` is a weighted heuristic, not a mathematically absolute truth. Higher is better.

                Current formula:

                ```text
                fairness_first_score =
                    100
                    - 1.35 * weighted_avg_distance_km
                    + 0.45 * share_within_10km_pct
                    + 0.20 * share_within_20km_pct
                    + 0.10 * share_within_5km_pct
                    - 8.0 * max(weighted_avg_distance_km - current_church_weighted_avg_distance_km, 0)
                ```

                Meaning of the inputs:

                - `weighted_avg_distance_km`: average member distance across the whole network after weighting by member counts. Lower is better for fairness.
                - `share_within_5km_pct`: share of all valid members estimated to be within 5 km.
                - `share_within_10km_pct`: share of all valid members estimated to be within 10 km.
                - `share_within_20km_pct`: share of all valid members estimated to be within 20 km.
                - `penalty vs current`: how many kilometers worse the weighted average distance is compared with the current church. If a candidate is better than current, this penalty is zero in the formula.

                How to read it:

                - A location can score well by keeping `weighted_avg_distance_km` low.
                - It also gets credit for bringing more members into practical travel bands like 10 km and 20 km.
                - It gets pushed down if it is materially worse than the current church on whole-network fairness.

                This score is meant to support shortlisting, not replace judgment about price, zoning, parking, transit, or building quality.
                """
            )
        fairness = build_fairness_shortlist(ranking, float(current_church["weighted_avg_distance_km"]))
        fairness_top = fairness.head(min(6, len(fairness))).copy()
        fairness_table = fairness_top.rename(
            columns={
                "search_area": "Area",
                "fairness_first_score": "Fairness-first score",
                "weighted_avg_distance_km": "Weighted avg distance (km)",
                "share_within_10km_pct": "Within 10 km (%)",
                "share_within_20km_pct": "Within 20 km (%)",
                "weighted_distance_penalty_km": "Penalty vs current (km)",
            }
        )[["Area", "Fairness-first score", "Weighted avg distance (km)", "Within 10 km (%)", "Within 20 km (%)", "Penalty vs current (km)"]].copy()
        for column in ["Fairness-first score", "Weighted avg distance (km)", "Within 10 km (%)", "Within 20 km (%)", "Penalty vs current (km)"]:
            fairness_table[column] = fairness_table[column].map(lambda value: round(float(value), 1))

        col1, col2 = st.columns([1.2, 1])
        with col1:
            fairness_chart = (
                alt.Chart(fairness_top)
                .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
                .encode(
                    x=alt.X("fairness_first_score:Q", title="Fairness-first score"),
                    y=alt.Y("search_area:N", sort=alt.SortField(field="fairness_first_score", order="descending"), title=None),
                    tooltip=[
                        alt.Tooltip("search_area:N", title="Area"),
                        alt.Tooltip("fairness_first_score:Q", title="Fairness-first score", format=".1f"),
                        alt.Tooltip("weighted_avg_distance_km:Q", title="Weighted avg distance (km)", format=".1f"),
                        alt.Tooltip("share_within_10km_pct:Q", title="Within 10 km (%)", format=".1f"),
                        alt.Tooltip("share_within_20km_pct:Q", title="Within 20 km (%)", format=".1f"),
                        alt.Tooltip("weighted_distance_penalty_km:Q", title="Penalty vs current (km)", format=".1f"),
                    ],
                )
                .properties(height=max(220, len(fairness_top) * 24), title="Fairness-first shortlist")
            )
            st.altair_chart(fairness_chart, use_container_width=True)
        with col2:
            st.dataframe(fairness_table, use_container_width=True, hide_index=True)

        st.markdown("#### Exact candidate property comparison")
        candidate_label = ctx.get("candidate_building_name") or "Candidate property"
        candidate_address = ctx.get("candidate_building_address") or "Address not set"
        candidate_summary = summarize_location(
            member_points,
            float(ctx["candidate_building_latitude"]),
            float(ctx["candidate_building_longitude"]),
            candidate_label,
        )
        exact_rows = [
            {
                "Location": f"{candidate_label} ({candidate_address})",
                "Weighted avg distance (km)": round(float(candidate_summary["weighted_avg_distance_km"]), 1),
                "Members within 5 km (%)": round(float(candidate_summary["share_within_5km_pct"]), 1),
                "Members within 10 km (%)": round(float(candidate_summary["share_within_10km_pct"]), 1),
                "Members within 20 km (%)": round(float(candidate_summary["share_within_20km_pct"]), 1),
            },
            {
                "Location": CURRENT_CHURCH_LABEL,
                "Weighted avg distance (km)": round(float(current_church["weighted_avg_distance_km"]), 1),
                "Members within 5 km (%)": round(float(current_church["share_within_5km_pct"]), 1),
                "Members within 10 km (%)": round(float(current_church["share_within_10km_pct"]), 1),
                "Members within 20 km (%)": round(float(current_church["share_within_20km_pct"]), 1),
            },
        ]
        st.dataframe(pd.DataFrame(exact_rows), use_container_width=True, hide_index=True)
        st.caption(
            f"Compared with {CURRENT_CHURCH_LABEL}, `{candidate_label}` changes weighted average distance by "
            f"{float(current_church['weighted_avg_distance_km']) - float(candidate_summary['weighted_avg_distance_km']):.1f} km, "
            f"the share within 10 km by {float(candidate_summary['share_within_10km_pct']) - float(current_church['share_within_10km_pct']):.1f} percentage points, "
            f"and the share within 20 km by {float(candidate_summary['share_within_20km_pct']) - float(current_church['share_within_20km_pct']):.1f} percentage points."
        )
        st.caption(
            "This block uses the exact candidate-property coordinates from the sidebar rather than the generic area presets."
        )

        ranking_table = ranking.rename(
            columns={
                "search_area": "Search area",
                "weighted_avg_distance_km": "Weighted avg distance (km)",
                "share_within_10km_pct": "Members within 10 km (%)",
            }
        )[["Search area", "Weighted avg distance (km)", "Members within 10 km (%)"]].copy()
        ranking_table["Weighted avg distance (km)"] = ranking_table["Weighted avg distance (km)"].map(lambda value: round(float(value), 1))
        ranking_table["Members within 10 km (%)"] = ranking_table["Members within 10 km (%)"].map(lambda value: round(float(value), 1))

        col1, col2 = st.columns([1.2, 1])
        with col1:
            distance_chart = (
                alt.Chart(ranking)
                .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
                .encode(
                    x=alt.X("weighted_avg_distance_km:Q", title="Weighted average distance (km)"),
                    y=alt.Y("search_area:N", sort=alt.SortField(field="weighted_avg_distance_km", order="ascending"), title=None),
                    tooltip=[
                        alt.Tooltip("search_area:N", title="Search area"),
                        alt.Tooltip("weighted_avg_distance_km:Q", title="Weighted avg distance (km)", format=".1f"),
                        alt.Tooltip("share_within_10km_pct:Q", title="Members within 10 km (%)", format=".1f"),
                    ],
                )
                .properties(height=max(260, len(ranking) * 24), title="Search-area ranking")
            )
            st.altair_chart(distance_chart, use_container_width=True)
        with col2:
            st.dataframe(ranking_table, use_container_width=True, hide_index=True)

        _render_point_map(
            ranking.assign(
                label=ranking["search_area"],
                radius_metric=ranking["share_within_10km_pct"] / 2,
                tooltip_label=ranking.apply(
                    lambda row: f"{row['search_area']}: {row['weighted_avg_distance_km']:.1f} km weighted avg distance, {row['share_within_10km_pct']:.1f}% within 10 km",
                    axis=1,
                ),
            ),
            "label",
        )

        st.markdown("### Closer-than-current comparison")
        st.caption(
            "Choose a current reference area, then compare how many members would be geographically closer to each candidate search area."
        )
        reference_area = st.selectbox(
            "Current reference area",
            options=selected_search_areas if selected_search_areas else list(SEARCH_AREA_COORDINATES.keys()),
            index=0,
            help="The baseline area used to ask: what share of members would be closer to each candidate than to this reference?",
        )

        comparison = compare_reference_vs_candidates(member_points, reference_area, selected_search_areas)
        if comparison.empty:
            st.info("Add at least one candidate area that differs from the current reference area.")
            return

        best_closer = comparison.iloc[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("Most members closer", str(best_closer["candidate_area"]), help="The candidate area that makes the largest share of members closer than the current reference area.")
        c2.metric("Members closer than current", f"{best_closer['closer_member_pct']:.1f}%", help="Share of all valid members whose estimated distance would be lower than to the selected reference area.")
        c3.metric("Average distance gain", f"{best_closer['avg_distance_gain_km']:.1f} km", help="Average change in distance across the whole member base. Positive is better; negative means the candidate is worse overall than the reference.")

        comparison_table = comparison.rename(
            columns={
                "candidate_area": "Candidate area",
                "closer_member_pct": "Members closer than current (%)",
                "avg_distance_gain_km": "Average distance gain (km)",
            }
        )[["Candidate area", "Members closer than current (%)", "Average distance gain (km)"]].copy()
        comparison_table["Members closer than current (%)"] = comparison_table["Members closer than current (%)"].map(lambda value: round(float(value), 1))
        comparison_table["Average distance gain (km)"] = comparison_table["Average distance gain (km)"].map(lambda value: round(float(value), 1))

        col1, col2 = st.columns([1.2, 1])
        with col1:
            closer_chart = (
                alt.Chart(comparison)
                .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
                .encode(
                    x=alt.X("closer_member_pct:Q", title="Members closer than current (%)"),
                    y=alt.Y("candidate_area:N", sort=alt.SortField(field="closer_member_pct", order="descending"), title=None),
                    tooltip=[
                        alt.Tooltip("candidate_area:N", title="Candidate area"),
                        alt.Tooltip("closer_member_pct:Q", title="Members closer than current (%)", format=".1f"),
                        alt.Tooltip("avg_distance_gain_km:Q", title="Average distance gain (km)", format=".1f"),
                    ],
                )
                .properties(height=max(240, len(comparison) * 24), title=f"Closer than {reference_area}")
            )
            st.altair_chart(closer_chart, use_container_width=True)
        with col2:
            st.dataframe(comparison_table, use_container_width=True, hide_index=True)
