from __future__ import annotations

from pathlib import Path
from math import asin, cos, radians, sin, sqrt

import pandas as pd
import streamlit as st

MUNICIPALITY_COORDINATES: dict[str, tuple[float, float]] = {
    "OSLO": (59.9139, 10.7522),
    "BÆRUM": (59.8940, 10.5260),
    "ÅS": (59.6640, 10.7940),
    "LILLESTRØM": (59.9560, 11.0490),
    "LØRENSKOG": (59.9290, 10.9550),
    "ASKER": (59.8350, 10.4350),
    "NORDRE FOLLO": (59.7500, 10.8800),
    "ULLENSAKER": (60.1700, 11.1750),
    "DRAMMEN": (59.7430, 10.2040),
    "NITTEDAL": (60.0570, 10.8810),
    "INDRE ØSTFOLD": (59.5530, 11.3250),
    "FREDRIKSTAD": (59.2180, 10.9290),
    "NES": (60.1220, 11.4660),
    "LIER": (59.7870, 10.2460),
    "KONGSVINGER": (60.1920, 11.9980),
    "TØNSBERG": (59.2670, 10.4070),
    "SANDEFJORD": (59.1310, 10.2160),
    "ØVRE EIKER": (59.7710, 9.9090),
    "HOLMESTRAND": (59.4860, 10.3170),
    "BERGEN": (60.3920, 5.3240),
    "MOSS": (59.4340, 10.6570),
    "EIDSVOLL": (60.3300, 11.2610),
    "AURSKOG-HØLAND": (59.8830, 11.5670),
    "RÆLINGEN": (59.9260, 11.0650),
    "NANNESTAD": (60.2230, 10.9510),
    "VESTBY": (59.6020, 10.7480),
    "NESODDEN": (59.8610, 10.6620),
    "FROGN": (59.6630, 10.6300),
    "ENEBAKK": (59.7640, 11.1440),
    "STAVANGER": (58.9700, 5.7330),
    "SARPSBORG": (59.2830, 11.1090),
    "SKIEN": (59.2090, 9.6080),
    "PORSGRUNN": (59.1410, 9.6560),
    "MODUM": (59.9680, 9.9820),
    "KONGSBERG": (59.6690, 9.6510),
    "HORTEN": (59.4140, 10.4850),
    "LARVIK": (59.0530, 10.0350),
    "RINGERIKE": (60.1680, 10.2560),
    "BODØ": (67.2800, 14.4050),
    "TRONDHEIM": (63.4300, 10.3950),
    "TROMSØ": (69.6490, 18.9560),
    "KRISTIANSAND": (58.1460, 7.9950),
    "HAMAR": (60.7950, 11.0680),
    "LILLEHAMMER": (61.1150, 10.4660),
    "GJØVIK": (60.7940, 10.6920),
    "ARENDAL": (58.4610, 8.7720),
    "GRIMSTAD": (58.3400, 8.5930),
    "SANDNES": (58.8520, 5.7360),
    "FARSUND": (58.0950, 6.8040),
    "VOSS": (60.6280, 6.4220),
    "KRISTIANSUND": (63.1100, 7.7280),
    "NARVIK": (68.4380, 17.4270),
    "STEINKJER": (64.0140, 11.4950),
}

OSLO_BYDEL_COORDINATES: dict[str, tuple[float, float]] = {
    "Gamle Oslo": (59.9070, 10.7790),
    "Grünerløkka": (59.9230, 10.7600),
    "Sagene": (59.9380, 10.7520),
    "St. Hanshaugen": (59.9270, 10.7380),
    "Frogner": (59.9220, 10.7060),
    "Ullern": (59.9250, 10.6560),
    "Vestre Aker": (59.9580, 10.6740),
    "Nordre Aker": (59.9500, 10.7820),
    "Bjerke": (59.9320, 10.8140),
    "Grorud": (59.9580, 10.8800),
    "Stovner": (59.9630, 10.9280),
    "Alna": (59.9230, 10.8550),
    "Østensjø": (59.8880, 10.8460),
    "Nordstrand": (59.8620, 10.8020),
    "Søndre Nordstrand": (59.8350, 10.8040),
}

SEARCH_AREA_COORDINATES: dict[str, tuple[float, float]] = {
    "Alna": (59.9230, 10.8550),
    "Furuset": (59.9270, 10.9120),
    "Grorud": (59.9580, 10.8820),
    "Stovner": (59.9620, 10.9260),
    "Helsfyr": (59.9130, 10.8040),
    "Bryn": (59.9080, 10.8120),
    "Økern": (59.9280, 10.8060),
    "Lørenskog": (59.9290, 10.9550),
    "Strømmen": (59.9520, 11.0070),
    "Ski": (59.7180, 10.8350),
}

CURRENT_CHURCH_COORDINATES: tuple[float, float] = (59.90235, 10.77186)
CURRENT_CHURCH_LABEL = "Current church (Alnafetgata 2)"
KNOWN_ADDRESS_COORDINATES: dict[str, tuple[float, float]] = {
    "alnafetgata 2, 0192 oslo": CURRENT_CHURCH_COORDINATES,
    "gransdalen 29, 1054 oslo": (59.9270, 10.9120),
}

OSLO_BYDEL_POSTCODE_EXACT: dict[str, str] = {
    "0650": "Gamle Oslo",
    "0656": "Gamle Oslo",
    "0657": "Gamle Oslo",
    "0658": "Gamle Oslo",
    "0659": "Gamle Oslo",
    "0660": "Gamle Oslo",
    "0661": "Gamle Oslo",
    "0662": "Gamle Oslo",
    "0663": "Gamle Oslo",
}

# Directional postcode-to-bydel mapping for Oslo.
OSLO_BYDEL_POSTCODE_RANGES: list[tuple[int, int, str]] = [
    (100, 199, "Gamle Oslo"),
    (200, 349, "Frogner"),
    (350, 379, "Frogner"),
    (380, 399, "Ullern"),
    (400, 449, "Nordre Aker"),
    (450, 499, "Sagene"),
    (500, 579, "Grünerløkka"),
    (580, 599, "Bjerke"),
    (660, 679, "Alna"),
    (680, 699, "Østensjø"),
    (700, 749, "Vestre Aker"),
    (750, 799, "Ullern"),
    (800, 859, "Vestre Aker"),
    (860, 899, "Nordre Aker"),
    (950, 979, "Grorud"),
    (980, 999, "Stovner"),
    (1000, 1089, "Alna"),
    (1100, 1149, "Østensjø"),
    (1150, 1179, "Nordstrand"),
    (1180, 1199, "Søndre Nordstrand"),
    (1200, 1249, "Østensjø"),
    (1250, 1269, "Nordstrand"),
    (1270, 1299, "Søndre Nordstrand"),
]


def estimate_oslo_bydel(postnummer: str) -> str | None:
    if not postnummer or not postnummer.isdigit():
        return None
    if postnummer in OSLO_BYDEL_POSTCODE_EXACT:
        return OSLO_BYDEL_POSTCODE_EXACT[postnummer]
    code = int(postnummer)
    for start, end, bydel in OSLO_BYDEL_POSTCODE_RANGES:
        if start <= code <= end:
            return bydel
    return None


@st.cache_data(show_spinner=False)
def load_member_distribution(base_path: str) -> pd.DataFrame:
    csv_path = Path(base_path) / "resources" / "member_distribution.csv"
    df = pd.read_csv(csv_path, dtype=str).fillna("")
    df.columns = [col.strip() for col in df.columns]
    df["postnummer"] = df["postnummer"].astype(str).str.strip().str.zfill(4)
    df.loc[df["postnummer"] == "0000", "postnummer"] = ""
    df["poststed"] = df["poststed"].astype(str).str.strip()
    df["Kommunenavn"] = df["Kommunenavn"].astype(str).str.strip().str.upper()
    df["valid_row"] = (df["postnummer"] != "") & (df["Kommunenavn"] != "")
    return df


def normalize_address(address: str) -> str:
    return " ".join((address or "").strip().lower().replace("\n", " ").split())


def lookup_known_address_coordinates(address: str) -> tuple[float, float] | None:
    normalized = normalize_address(address)
    if not normalized:
        return None
    return KNOWN_ADDRESS_COORDINATES.get(normalized)


def build_municipality_distribution(df: pd.DataFrame) -> pd.DataFrame:
    valid = df[df["valid_row"]].copy()
    municipality = (
        valid.groupby("Kommunenavn")
        .size()
        .reset_index(name="member_count")
        .sort_values(["member_count", "Kommunenavn"], ascending=[False, True])
        .rename(columns={"Kommunenavn": "municipality"})
    )
    total = int(municipality["member_count"].sum())
    municipality["share_pct"] = municipality["member_count"] / total * 100 if total else 0.0
    municipality["lat"] = municipality["municipality"].map(lambda x: MUNICIPALITY_COORDINATES.get(x, (None, None))[0])
    municipality["lon"] = municipality["municipality"].map(lambda x: MUNICIPALITY_COORDINATES.get(x, (None, None))[1])
    return municipality


def build_oslo_bydel_distribution(df: pd.DataFrame) -> tuple[pd.DataFrame, int, pd.DataFrame]:
    oslo = df[(df["valid_row"]) & (df["Kommunenavn"] == "OSLO")].copy()
    oslo["bydel"] = oslo["postnummer"].map(estimate_oslo_bydel)
    matched = oslo[oslo["bydel"].notna()].copy()
    bydel = (
        matched.groupby("bydel")
        .size()
        .reset_index(name="member_count")
        .sort_values(["member_count", "bydel"], ascending=[False, True])
    )
    total = int(bydel["member_count"].sum())
    bydel["share_pct"] = bydel["member_count"] / total * 100 if total else 0.0
    bydel["share_of_all_valid_pct"] = bydel["member_count"] / int(df["valid_row"].sum()) * 100 if int(df["valid_row"].sum()) else 0.0
    bydel["lat"] = bydel["bydel"].map(lambda x: OSLO_BYDEL_COORDINATES.get(x, (None, None))[0])
    bydel["lon"] = bydel["bydel"].map(lambda x: OSLO_BYDEL_COORDINATES.get(x, (None, None))[1])
    unmatched_rows = oslo[oslo["bydel"].isna()][["postnummer", "poststed", "Kommunenavn"]].copy()
    unmatched = int(len(unmatched_rows))
    return bydel, unmatched, unmatched_rows


def build_member_point_distribution(df: pd.DataFrame) -> pd.DataFrame:
    valid = df[df["valid_row"]].copy()
    oslo = valid[valid["Kommunenavn"] == "OSLO"].copy()
    non_oslo = valid[valid["Kommunenavn"] != "OSLO"].copy()

    oslo["area_name"] = oslo["postnummer"].map(estimate_oslo_bydel).fillna("Oslo (unmatched)")
    oslo["lat"] = oslo["area_name"].map(lambda x: OSLO_BYDEL_COORDINATES.get(x, MUNICIPALITY_COORDINATES["OSLO"])[0])
    oslo["lon"] = oslo["area_name"].map(lambda x: OSLO_BYDEL_COORDINATES.get(x, MUNICIPALITY_COORDINATES["OSLO"])[1])

    non_oslo["area_name"] = non_oslo["Kommunenavn"]
    non_oslo["lat"] = non_oslo["Kommunenavn"].map(lambda x: MUNICIPALITY_COORDINATES.get(x, (None, None))[0])
    non_oslo["lon"] = non_oslo["Kommunenavn"].map(lambda x: MUNICIPALITY_COORDINATES.get(x, (None, None))[1])

    combined = pd.concat(
        [
            oslo[["area_name", "lat", "lon"]],
            non_oslo[["area_name", "lat", "lon"]],
        ],
        ignore_index=True,
    ).dropna(subset=["lat", "lon"])

    points = (
        combined.groupby(["area_name", "lat", "lon"])
        .size()
        .reset_index(name="member_count")
        .sort_values(["member_count", "area_name"], ascending=[False, True])
    )
    return points


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_km = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    return 2 * radius_km * asin(sqrt(a))


def weighted_center(points: pd.DataFrame) -> tuple[float, float]:
    total = float(points["member_count"].sum())
    if total <= 0:
        return MUNICIPALITY_COORDINATES["OSLO"]
    lat = float((points["lat"] * points["member_count"]).sum() / total)
    lon = float((points["lon"] * points["member_count"]).sum() / total)
    return lat, lon


def rank_search_areas(points: pd.DataFrame, area_names: list[str]) -> pd.DataFrame:
    rows: list[dict[str, float | str]] = []
    total_members = max(float(points["member_count"].sum()), 1.0)
    for name in area_names:
        if name not in SEARCH_AREA_COORDINATES:
            continue
        lat, lon = SEARCH_AREA_COORDINATES[name]
        weighted_distance = (
            points.apply(lambda row: haversine_km(float(row["lat"]), float(row["lon"]), lat, lon) * float(row["member_count"]), axis=1).sum()
            / total_members
        )
        within_5km = (
            points.apply(lambda row: float(row["member_count"]) if haversine_km(float(row["lat"]), float(row["lon"]), lat, lon) <= 5 else 0.0, axis=1).sum()
            / total_members
            * 100
        )
        within_10km = (
            points.apply(lambda row: float(row["member_count"]) if haversine_km(float(row["lat"]), float(row["lon"]), lat, lon) <= 10 else 0.0, axis=1).sum()
            / total_members
            * 100
        )
        within_20km = (
            points.apply(lambda row: float(row["member_count"]) if haversine_km(float(row["lat"]), float(row["lon"]), lat, lon) <= 20 else 0.0, axis=1).sum()
            / total_members
            * 100
        )
        rows.append(
            {
                "search_area": name,
                "weighted_avg_distance_km": weighted_distance,
                "share_within_5km_pct": within_5km,
                "share_within_10km_pct": within_10km,
                "share_within_20km_pct": within_20km,
                "lat": lat,
                "lon": lon,
            }
        )
    return pd.DataFrame(rows).sort_values(["weighted_avg_distance_km", "search_area"], ascending=[True, True])


def summarize_location(points: pd.DataFrame, lat: float, lon: float, label: str) -> dict[str, float | str]:
    total_members = max(float(points["member_count"].sum()), 1.0)
    weighted_distance = 0.0
    within_10km = 0.0
    within_5km = 0.0
    within_20km = 0.0
    for _, row in points.iterrows():
        members = float(row["member_count"])
        distance = haversine_km(float(row["lat"]), float(row["lon"]), lat, lon)
        weighted_distance += distance * members
        if distance <= 10:
            within_10km += members
        if distance <= 5:
            within_5km += members
        if distance <= 20:
            within_20km += members
    return {
        "label": label,
        "weighted_avg_distance_km": weighted_distance / total_members,
        "share_within_10km_pct": within_10km / total_members * 100,
        "share_within_5km_pct": within_5km / total_members * 100,
        "share_within_20km_pct": within_20km / total_members * 100,
        "lat": lat,
        "lon": lon,
    }


def compare_reference_vs_candidates(points: pd.DataFrame, reference_name: str, candidate_names: list[str]) -> pd.DataFrame:
    if reference_name not in SEARCH_AREA_COORDINATES:
        return pd.DataFrame()
    ref_lat, ref_lon = SEARCH_AREA_COORDINATES[reference_name]
    rows: list[dict[str, float | str]] = []
    total_members = max(float(points["member_count"].sum()), 1.0)
    for candidate_name in candidate_names:
        if candidate_name not in SEARCH_AREA_COORDINATES or candidate_name == reference_name:
            continue
        cand_lat, cand_lon = SEARCH_AREA_COORDINATES[candidate_name]
        closer_member_count = 0.0
        weighted_distance_gain = 0.0
        for _, row in points.iterrows():
            members = float(row["member_count"])
            member_lat = float(row["lat"])
            member_lon = float(row["lon"])
            ref_distance = haversine_km(member_lat, member_lon, ref_lat, ref_lon)
            cand_distance = haversine_km(member_lat, member_lon, cand_lat, cand_lon)
            if cand_distance < ref_distance:
                closer_member_count += members
            weighted_distance_gain += (ref_distance - cand_distance) * members
        rows.append(
            {
                "candidate_area": candidate_name,
                "closer_member_pct": closer_member_count / total_members * 100,
                "avg_distance_gain_km": weighted_distance_gain / total_members,
                "lat": cand_lat,
                "lon": cand_lon,
            }
        )
    return pd.DataFrame(rows).sort_values(["closer_member_pct", "avg_distance_gain_km"], ascending=[False, False])


def build_fairness_shortlist(ranking: pd.DataFrame, baseline_weighted_distance_km: float) -> pd.DataFrame:
    if ranking.empty:
        return ranking
    scored = ranking.copy()
    # Fairness-first means keeping overall burden low while still improving practical access bands.
    scored["weighted_distance_penalty_km"] = scored["weighted_avg_distance_km"] - baseline_weighted_distance_km
    scored["fairness_first_score"] = (
        100
        - scored["weighted_avg_distance_km"] * 1.35
        + scored["share_within_10km_pct"] * 0.45
        + scored["share_within_20km_pct"] * 0.20
        + scored["share_within_5km_pct"] * 0.10
        - scored["weighted_distance_penalty_km"].clip(lower=0) * 8.0
    )
    return scored.sort_values(
        ["fairness_first_score", "weighted_avg_distance_km", "share_within_10km_pct"],
        ascending=[False, True, False],
    )
