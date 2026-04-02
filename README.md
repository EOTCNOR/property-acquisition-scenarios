# Gransdalen 29 Scenario Tool

This repository contains a Streamlit decision-support app for evaluating the Gransdalen 29 purchase and transition scenarios.

## Requirements

- Python `3.9+` recommended
- `pip` available in your shell

## Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run The App

From the repository root:

```bash
streamlit run streamlit_app.py
```

Streamlit will print a local URL, typically:

```text
http://localhost:8501
```

Open that URL in your browser.

If port `8501` is already in use, run:

```bash
streamlit run streamlit_app.py --server.port 8502
```

## Repository Layout

- [streamlit_app.py](/home/abyot/coding/EOTCNOR/Gransdalen29/streamlit_app.py): thin Streamlit entrypoint
- [app/app.py](/home/abyot/coding/EOTCNOR/Gransdalen29/app/app.py): top-level app composition
- [app/tabs/](/home/abyot/coding/EOTCNOR/Gransdalen29/app/tabs): tab render modules
- [app/config.py](/home/abyot/coding/EOTCNOR/Gransdalen29/app/config.py): JSON-backed config loading
- [app/finance.py](/home/abyot/coding/EOTCNOR/Gransdalen29/app/finance.py): loan and payment calculations
- [app/formatting.py](/home/abyot/coding/EOTCNOR/Gransdalen29/app/formatting.py): display formatting helpers
- [config/app_defaults.json](/home/abyot/coding/EOTCNOR/Gransdalen29/config/app_defaults.json): default values and field descriptions
- [config/ui_labels.json](/home/abyot/coding/EOTCNOR/Gransdalen29/config/ui_labels.json): UI labels and captions

## Notes

- The app is a planning tool, not a legal, valuation, architectural, or engineering opinion.
- Cross-tab floor-planning inputs are stored in Streamlit session state during runtime.
