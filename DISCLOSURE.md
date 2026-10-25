# Data and AI disclosure statement

## Data

All data come from public, citable sources:

- **Central Statistics Office (Ireland)**, *Data Centres Metered Electricity Consumption 2025* (7 July
  2026), Tables 1 and 2. Measured from electricity meters. CC BY 4.0.
- **International Energy Agency**, *Energy and AI* (2025) and *Key Questions on Energy and AI* (2026).
  Modelled estimates and projections. CC BY 4.0.
- **Lawrence Berkeley National Laboratory**, *2024 United States Data Center Energy Usage Report* and its
  *2025 Update* (2026). Modelled estimates and projections.
- **Congressional Research Service**, *Data Centers and Their Energy Consumption: Frequently Asked
  Questions* (R48646), citing EPRI. Estimate of AI's share of data centre electricity.

The figures were transcribed by hand from the published tables and report text into `data/source/`, using
the publishers' own values and rounding. No values were estimated, interpolated or edited. Every processed
file is regenerated from the source samples by `src/pipeline.py`, documented in `data/DATA_DICTIONARY.md`.

Most figures measure **data centres**, not AI. The AI-specific figures are IEA and EPRI modelled
estimates; no source used here meters AI's own electricity consumption. The app says so on screen.

## AI use

Claude (Anthropic) was used through the claude.ai chat interface. It found and checked the data sources,
transcribed the source samples, and wrote the data pipeline, chart code, Streamlit app, README, data
dictionary and this repository's documentation. Each substantive use, and the check applied to it, is
recorded in `PROVENANCE_MATRIX.md`.

Several of those checks failed and led to changes: an outdated CSO release replaced by the revised 2025
release; superseded IEA and LBNL figures replaced by their 2026 editions; incorrect rounding years in the
data dictionary; unreadable chart labels; a distorted projection axis; overlapping and clipped labels; and
three chart titles that claimed more than the data showed.

Group members' own uses of AI are recorded in their rows of the provenance matrix.
