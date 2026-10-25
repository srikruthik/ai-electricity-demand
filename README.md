# Is AI becoming a significant driver of electricity demand?

An interactive data narrative for 36104 Data Visualisation and Narratives, Assignment 3.

## Question

Is AI becoming a significant driver of electricity demand?

**Why it is arguable.** The same data support different answers. Read as a share of total use, data
centres look minor: about 1.5% of world electricity in 2024. Read as a share of *growth*, they look
dominant: in Ireland they supplied 77% of the increase in metered electricity demand from 2015 to 2025,
and the IEA projects nearly half of US demand growth to 2030. The app lets the reader switch between the
two measures. And because no source meters AI's own electricity use, a reader can accept that data
centres drive demand and still answer "no" for AI, even though AI-focused data centres grew fastest in
2025.

## Persona

**A demand-forecasting analyst at a national electricity system operator.** They must decide whether
data centre load should be modelled as its own fast-growing demand category in the next long-term demand
forecast, rather than folded into general commercial demand. They need to know how large and how fast
data centre demand has grown where it is measured, how much of total growth it explains, and whether a
grid like Ireland's is an outlier or an early sign of what others will face.

## User stories

1. **As a** demand-forecasting analyst, **I want** to see how data centre electricity use has grown
   against every other metered customer, **so that** I can judge whether it behaves like a separate demand
   driver.
   *In the app:* tab 1, the trend chart and the year-on-year change chart, with the **Years to compare**
   slider and the **Show consumption as** switch between gigawatt hours and an index.

2. **As a** demand-forecasting analyst, **I want** to see how much of the increase in demand over a period I
   choose came from data centres, **so that** I can decide whether they need their own growth component in
   the forecast.
   *In the app:* tab 1, the share chart and the change-by-customer-type chart, both driven by the
   **Years to compare** slider; the opening screen's **How the 77% is calculated** panel; and the
   **Download these years as CSV** button.

3. **As a** demand-forecasting analyst, **I want** to compare Ireland with the United States, other
   economies and the world, by share of use and by share of demand growth, and see the published
   projections, **so that** I can judge whether Ireland is an outlier or an early signal for other grids.
   *In the app:* tab 2, the **Measure significance as** switch, the **Places to compare** filter and the
   **Projections for** selector; tab 3 for the AI-specific evidence.

## Answer the app gives

Locally, yes. Globally, not yet, though it is heading that way. And AI is the fastest-growing part,
though its share of data centre electricity is estimated rather than measured. See the app's opening
screen and *What these data cannot show*.

## Running the app

Python 3.11 or 3.12 (pandas 3 requires 3.11 or later).

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Rebuilding the data

```bash
python -m src.pipeline           # regenerate data/processed from data/source
python -m src.pipeline --check   # confirm the committed processed files match a fresh rebuild
python -m unittest discover tests  # prove each validation check rejects bad data
python -m src.trace                # show how the headline 77% is calculated
```

## Repository contents

| Path | Contents |
|---|---|
| `app.py` | Streamlit application |
| `src/pipeline.py` | Validates the source samples and builds every processed file |
| `src/trace.py` | Prints how the headline 77% is calculated, from the processed data |
| `src/style.py` | Shared colour palette |
| `src/charts_ireland.py` | Tab 1 charts: trend, share, change, year on year |
| `src/charts_global.py` | Tab 2 charts: comparison and projections |
| `src/charts_ai.py` | Tab 3 chart: AI-specific growth |
| `tests/test_pipeline.py` | Feeds each validation check the broken data it exists to catch |
| `data/source/` | Source samples, transcribed from the cited publications |
| `data/processed/` | Files the app reads |
| `data/DATA_DICTIONARY.md` | Every dataset: source, URL, licence, columns, units, key, coverage, transform |
| `PROVENANCE_MATRIX.md` | One row per substantive AI use |
| `DISCLOSURE.md` | Data and AI disclosure statement |
