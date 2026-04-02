# Session Handoff

Date: 2 April 2026

## Current State

The repository now contains a working Streamlit decision-support tool renamed to `Property Acquisition Scenarios Tool`.

The app is no longer Gransdalen-specific in its framing. It is now organized around a reusable acquisition workflow:

- executive summary
- screening and diligence
- member geography
- floor-based space planning
- floor-based renovation planning
- floor-based income planning
- mortgage, overlap, scenarios, and thresholds

The codebase is now modularized under `app/` with dedicated tab modules, and the repository has been initialized as a Git repo.

## Main App Structure

Main entrypoint:

- [/home/abyot/coding/EOTCNOR/Gransdalen29/streamlit_app.py](/home/abyot/coding/EOTCNOR/Gransdalen29/streamlit_app.py)

Core composition:

- [/home/abyot/coding/EOTCNOR/Gransdalen29/app/app.py](/home/abyot/coding/EOTCNOR/Gransdalen29/app/app.py)

Config:

- [/home/abyot/coding/EOTCNOR/Gransdalen29/config/app_defaults.json](/home/abyot/coding/EOTCNOR/Gransdalen29/config/app_defaults.json)
- [/home/abyot/coding/EOTCNOR/Gransdalen29/config/ui_labels.json](/home/abyot/coding/EOTCNOR/Gransdalen29/config/ui_labels.json)

Main tab modules:

- [/home/abyot/coding/EOTCNOR/Gransdalen29/app/tabs/executive_summary.py](/home/abyot/coding/EOTCNOR/Gransdalen29/app/tabs/executive_summary.py)
- [/home/abyot/coding/EOTCNOR/Gransdalen29/app/tabs/screening.py](/home/abyot/coding/EOTCNOR/Gransdalen29/app/tabs/screening.py)
- [/home/abyot/coding/EOTCNOR/Gransdalen29/app/tabs/member_geography.py](/home/abyot/coding/EOTCNOR/Gransdalen29/app/tabs/member_geography.py)
- [/home/abyot/coding/EOTCNOR/Gransdalen29/app/tabs/hall.py](/home/abyot/coding/EOTCNOR/Gransdalen29/app/tabs/hall.py)
- [/home/abyot/coding/EOTCNOR/Gransdalen29/app/tabs/renovation.py](/home/abyot/coding/EOTCNOR/Gransdalen29/app/tabs/renovation.py)
- [/home/abyot/coding/EOTCNOR/Gransdalen29/app/tabs/income.py](/home/abyot/coding/EOTCNOR/Gransdalen29/app/tabs/income.py)
- [/home/abyot/coding/EOTCNOR/Gransdalen29/app/tabs/mortgage.py](/home/abyot/coding/EOTCNOR/Gransdalen29/app/tabs/mortgage.py)
- [/home/abyot/coding/EOTCNOR/Gransdalen29/app/tabs/operations.py](/home/abyot/coding/EOTCNOR/Gransdalen29/app/tabs/operations.py)
- [/home/abyot/coding/EOTCNOR/Gransdalen29/app/tabs/scenario_paths.py](/home/abyot/coding/EOTCNOR/Gransdalen29/app/tabs/scenario_paths.py)
- [/home/abyot/coding/EOTCNOR/Gransdalen29/app/tabs/thresholds.py](/home/abyot/coding/EOTCNOR/Gransdalen29/app/tabs/thresholds.py)

Member geography helpers:

- [/home/abyot/coding/EOTCNOR/Gransdalen29/app/member_distribution.py](/home/abyot/coding/EOTCNOR/Gransdalen29/app/member_distribution.py)

## Current Tabs

Tabs currently in the app:

- Executive Summary
- Screening Framework
- Member Geography
- Renovation Cost
- Income Generation
- Space Utilization
- Mortgage Plan
- Portfolio Overlap
- Scenario Paths
- Thresholds

`Risk Assessment` was removed as a separate tab and merged into `Screening Framework` as a financial-risk snapshot.

`Due Diligence` was also merged into `Screening Framework`.

## Most Important Changes In This Session

- Fixed the Streamlit blank-screen issue by changing the entrypoint to explicitly call `run()`.
- Finished the modular refactor so `app/app.py` is now a thin composition layer.
- Added a new `Member Geography` tab using `resources/member_distribution.csv`.
- Added municipality and Oslo bydel analysis, including sorted charts, tables, and map views.
- Added an estimated member center-of-gravity workflow and candidate-area ranking.
- Added fairness-first location ranking for whole-membership decision-making.
- Added exact candidate-property comparison using sidebar address/lat/lon.
- Added current-church comparison against `Alnafetgata 2`.
- Merged `Due Diligence` into `Screening Framework`.
- Merged the useful financial-risk lens into `Screening Framework` and removed the separate `Risk Assessment` tab.
- Reworked `Space Utilization`, `Renovation Cost`, and `Income Generation` so they now form one floor-based workflow:
  - what each floor is for
  - what each floor costs
  - what each floor earns
- Added a new `Executive Summary` tab for board-level reading.
- Moved the main board-facing labels, section headings, and sidebar terms into `config/ui_labels.json` so church-specific wording can be edited without touching code.
- Initialized Git and added a practical `.gitignore` that excludes `/docs`, `/resources`, and common local/runtime noise.

## Member Geography State

The member geography work is one of the main additions in this session.

Data source:

- [/home/abyot/coding/EOTCNOR/Gransdalen29/resources/member_distribution.csv](/home/abyot/coding/EOTCNOR/Gransdalen29/resources/member_distribution.csv)

Current behavior includes:

- municipality-level member count and share
- Oslo bydel estimate from postcode mapping
- bydel chart/table sorted by member count
- both `% of matched Oslo rows` and `% of all valid members`
- candidate search-area ranking
- fairness-first shortlist
- exact property comparison against the current church
- 5 km / 10 km / 20 km reach metrics

Important modeling note:

- Oslo `bydel` is estimated from postcodes and is suitable for directional search planning, not official district reporting

The earlier unmatched `065x` Oslo rows were corrected and now map to `Gamle Oslo`.

## Screening / Summary State

`Screening Framework` is now the main gateway tab.

It now includes:

- confirmed diligence facts
- heuristic screening assumptions
- gateway summary
- financial-risk snapshot
- diligence checklist

The earlier inconsistency where the bottom diligence summary ignored the selected checklist states has been fixed.

The top gateway signals and the bottom diligence summary now use the same underlying logic.

The new `Executive Summary` tab is intended for board and elder review. It reuses the live outputs from the detailed tabs rather than running a second model.

## Floor-Based Planning State

The floor-based workflow is now consistent across three tabs:

- `Space Utilization`
- `Renovation Cost`
- `Income Generation`

Current logic:

- `Space Utilization` defines the intended use of each floor
- `Renovation Cost` uses the same floors for floor-level scope and building-wide cost
- `Income Generation` uses the same floors and lets income be zero on floors that do not realistically produce income

This was done specifically to make the story easier for decision makers to follow.

## Config / Language State

The app now has a usable configuration surface for the main board-facing language in:

- [/home/abyot/coding/EOTCNOR/Gransdalen29/config/ui_labels.json](/home/abyot/coding/EOTCNOR/Gransdalen29/config/ui_labels.json)

Currently config-driven:

- app title and caption
- tab names
- major sidebar labels
- executive-summary headings and metrics
- screening-framework headings
- main section headings in space / renovation / income

Not fully config-driven yet:

- many lower-level inline field labels
- most tooltips
- deeper labels inside mortgage / overlap / scenario / threshold / member-geography details

This was an intentional cutoff. The focus was to make the visible, tone-setting language editable without forcing a risky full-label rewrite in one session.

## Verification Done

Repeated verification used during the session:

```bash
python -m py_compile streamlit_app.py app/app.py app/tabs/*.py
```

The code compiled successfully after the latest changes.

Important limitation:

- true `streamlit run` browser/socket verification was not available in the sandbox
- the user verified the app manually in their own environment after the earlier blank-screen fix

## Repository State

The repository has been initialized as Git.

The user has already pushed at least once during this session history.

Current deployment-related files still carry historical names on disk in some places, for example:

- [/home/abyot/coding/EOTCNOR/Gransdalen29/deploy/gransdalen29.service](/home/abyot/coding/EOTCNOR/Gransdalen29/deploy/gransdalen29.service)

The contents have been made more generic, but file/path renaming was not the priority.

## Best Next Steps

If work continues later, the most sensible next improvements are:

1. Replace the now-configurable board-facing labels in `config/ui_labels.json` with the church’s own language.
2. Decide whether the deployment filenames and service names should also be renamed away from historical Gransdalen naming.
3. Continue grounding detailed financial assumptions against real operating history where possible.
4. If needed, push more of the deeper tab labels into config later, but only after the church-specific top-level language is settled.
