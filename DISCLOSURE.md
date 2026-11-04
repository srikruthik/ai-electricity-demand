# Data and AI disclosure statement

## Data

All data come from public, citable sources:

- **Central Statistics Office (Ireland)**, *Data Centres Metered Electricity Consumption 2025* (7 July 2026), Tables 1 and 2. Measured from electricity meters. CC BY 4.0.
- **International Energy Agency**, *Energy and AI* (2025) and *Key Questions on Energy and AI* (2026). Modelled estimates and projections. CC BY 4.0.
- **Lawrence Berkeley National Laboratory**, *2024 United States Data Center Energy Usage Report* and its *2025 Update* (2026). Modelled estimates and projections.
- **Congressional Research Service**, *Data Centers and Their Energy Consumption: Frequently Asked Questions* (R48646), citing EPRI. Estimate of AI's share of data centre electricity.

The figures were transcribed by hand from the published tables and report text into `data/source/`, using the publishers' own values and rounding. No values were estimated, interpolated or edited. Every processed file is regenerated from the source samples by `src/pipeline.py`, documented in `data/DATA_DICTIONARY.md`.

Most figures measure **data centres**, not AI. The AI-specific figures are IEA and EPRI modelled estimates; no source used here meters AI's own electricity consumption. The app says so on screen.

## AI use

Microsoft Copilot was used by Kota Srikruthik to assist with identifying and checking data sources, preparing source data, researching published estimates, developing the data validation pipeline, and building the Streamlit application and project documentation.

Other group members used ChatGPT (OpenAI) for their respective contributions to the Ireland visualisations, global comparison charts, AI-specific analysis and accessibility review.

Each substantive AI use, including the artefact, tool, contribution, verification method and outcome, is documented in `PROVENANCE_MATRIX.md`.

AI-generated outputs were not accepted without review. Verification identified issues that led to changes, including an outdated CSO release, superseded IEA and LBNL figures, incorrect rounding-year documentation, unreadable chart labels, a distorted projection axis, overlapping and clipped labels, and chart titles that overstated what the data showed.

The group independently checked the relevant figures, calculations, data transformations, visualisations and application behaviour. The provenance matrix records the checks and their outcomes.
