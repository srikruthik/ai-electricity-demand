# Data dictionary

Every file the app reads is in `data/processed/` and is regenerated from `data/source/` by
`python -m src.pipeline`. `python -m src.pipeline --check` confirms the committed processed files match a
fresh rebuild byte for byte.

Data last refreshed: **2026-10-20**.

## How the source samples were made

The publishers release these figures as web tables, spreadsheets and report text rather than through an
API. Each source sample was transcribed by hand from the cited table or page into CSV, keeping the
publisher's own values, units and rounding. Nothing was estimated or interpolated. The pipeline then checks
the CSO samples against each other (see *Validation*), which would catch most transcription errors.

---

## Source samples (`data/source/`)

### `cso_mec02_annual.csv`

| Field | Value |
|---|---|
| Source | Central Statistics Office (Ireland), *Data Centres Metered Electricity Consumption 2025*, Table 1 (also published as PxStat table MEC02) |
| URL | https://www.cso.ie/en/releasesandpublications/ep/p-dcmec/datacentresmeteredelectricityconsumption2025/keyfindings/ |
| Spreadsheet | https://www.cso.ie/en/media/csoie/releasespublications/documents/ep/datacentresmeteredelectricityconsumption/2025/P-DCMEC2025TBL1.xlsx |
| Licence | Creative Commons Attribution 4.0 (CSO copyright and re-use policy) |
| Published | 7 July 2026 |
| Primary key | `year` |
| Time coverage | 2015-2025, annual |
| Latest observation | 2025 |
| Transform | Transcribed from Table 1. No changes. |

| Column | Type | Unit | Description |
|---|---|---|---|
| `year` | integer | year | Calendar year |
| `data_centres_gwh` | integer | GWh | Metered electricity consumption by data centres |
| `other_metered_customers_gwh` | integer | GWh | Metered consumption by all other customers |
| `total_gwh` | integer | GWh | Total metered electricity consumption, as published |

### `cso_mec02_quarterly.csv`

| Field | Value |
|---|---|
| Source | Central Statistics Office (Ireland), *Data Centres Metered Electricity Consumption 2025*, Table 2 |
| URL | https://www.cso.ie/en/releasesandpublications/ep/p-dcmec/datacentresmeteredelectricityconsumption2025/keyfindings/ |
| Spreadsheet | https://www.cso.ie/en/media/csoie/releasespublications/documents/ep/datacentresmeteredelectricityconsumption/2025/P-DCMEC2025TBL2.xlsx |
| Licence | Creative Commons Attribution 4.0 |
| Published | 7 July 2026 |
| Primary key | `year`, `quarter` |
| Time coverage | Q1 2015 - Q4 2025, quarterly |
| Latest observation | Q4 2025 |
| Transform | Transcribed from Table 2, reshaped from one row per year to one row per quarter. Used only to validate the annual table; the app does not display it. |

| Column | Type | Unit | Description |
|---|---|---|---|
| `year` | integer | year | Calendar year |
| `quarter` | string | - | `Q1` (Jan-Mar) to `Q4` (Oct-Dec) |
| `data_centres_gwh` | integer | GWh | Metered electricity consumption by data centres in the quarter |

### `published_estimates.csv`

| Field | Value |
|---|---|
| Sources | International Energy Agency, *Energy and AI* (April 2025) and *Key Questions on Energy and AI* (16 April 2026) with its press release; Lawrence Berkeley National Laboratory, *2024 United States Data Center Energy Usage Report* and *United States Data Center Energy Usage Report: 2025 Update* (June 2026); Congressional Research Service, *Data Centers and Their Energy Consumption: Frequently Asked Questions* (R48646), citing EPRI |
| URLs | Per row, in the `url` column |
| Licence | IEA: Creative Commons Attribution 4.0. LBNL 2025 Update (published June 2026): Creative Commons Attribution 4.0, confirmed by the eScholarship publication record (https://escholarship.org/uc/item/33m6w3x0). LBNL 2024 report: licence not independently verified; figures attributed to the original report. CRS: US Government work, public domain. |
| Primary key | `estimate_id` |
| Time coverage | 2023-2035 (estimates for 2023-2025; projections for 2030-2035) |
| Latest observation | 2025 for estimates; projections run to 2035 |
| Transform | Each figure transcribed from the text of the cited publication into one row, keeping the publisher's rounding and wording ("around", "more than", "nearly") in `qualifier`. |

| Column | Type | Unit | Description |
|---|---|---|---|
| `estimate_id` | string | - | Unique identifier; prefix names the source and edition (`iea25`, `iea26`, `lbnl24`, `lbnl26`, `epri`) |
| `jurisdiction` | string | - | `World`, `United States`, `Advanced economies` or `Emerging and developing economies` |
| `subject` | string | - | What is measured: `All data centres`, `AI-focused data centres`, `AI workloads` or `All electricity demand` |
| `year` | integer | year | Year the figure refers to; for shares of growth, the end of the 2024-2030 period |
| `metric` | string | - | `data_centre_electricity`, `data_centre_share_of_electricity`, `data_centre_share_of_demand_growth`, `annual_growth_rate` or `ai_share_of_data_centre_electricity` |
| `value` | number | see `unit` | The published figure |
| `unit` | string | - | `TWh` or `percent` |
| `qualifier` | string | - | The publisher's approximation word (`around`, `more than`, `nearly`); blank when the figure is stated exactly |
| `case` | string | - | `estimate`, `base case`, `reference case`, `lowest case`, `highest case`, `low bound`, `high bound`, `low estimate`, `high estimate` |
| `method` | string | - | `modelled` (an estimate of the past) or `projection` (a scenario for the future) |
| `source_short` | string | - | Short citation shown on charts, e.g. `IEA (2026)` |
| `publisher` | string | - | Organisation that published the figure |
| `publication` | string | - | Publication title |
| `url` | string | - | Where the figure appears |

---

## Processed files (`data/processed/`)

### `ireland_annual.csv`

| Field | Value |
|---|---|
| Built from | `cso_mec02_annual.csv` |
| Primary key | `year` |
| Time coverage | 2015-2025 |
| Latest observation | 2025 |
| Transform | Renames `other_metered_customers_gwh` to `other_gwh`. Adds `data_centre_share_pct` = `data_centres_gwh` / `total_gwh` x 100, rounded to one decimal place, and the change from the previous year for each customer type (blank for 2015). |

| Column | Type | Unit | Description |
|---|---|---|---|
| `year` | integer | year | Calendar year |
| `data_centres_gwh` | integer | GWh | As in source |
| `other_gwh` | integer | GWh | As `other_metered_customers_gwh` in source |
| `total_gwh` | integer | GWh | As in source |
| `data_centre_share_pct` | number | percent | Data centres' share of total metered consumption |
| `dc_change_gwh` | integer | GWh | Change in data centre consumption from the previous year |
| `other_change_gwh` | integer | GWh | Change in other customers' consumption from the previous year |

Values the app computes from this file at display time: the change between two selected years for each
customer type, data centres' share of the net increase, and the index (first selected year = 100).

### `jurisdiction_share.csv`

| Field | Value |
|---|---|
| Built from | `ireland_annual.csv` (latest year) and the `data_centre_share_of_electricity` rows of `published_estimates.csv` |
| Primary key | `jurisdiction` |
| Time coverage | 2023-2025 (one year per jurisdiction) |
| Latest observation | Ireland 2025, World 2024, United States 2023 |
| Transform | Takes Ireland's latest computed share and the published shares, adds a display label with the publisher's qualifier, and sorts by share, highest first. |

| Column | Type | Unit | Description |
|---|---|---|---|
| `jurisdiction` | string | - | Place |
| `period` | string | year | Year of the figure |
| `share_pct` | number | percent | Data centre share of electricity consumption |
| `label` | string | - | Value as displayed, with qualifier |
| `basis` | string | - | `metered` or `modelled` |
| `source` | string | - | Short citation |

### `growth_share.csv`

| Field | Value |
|---|---|
| Built from | `ireland_annual.csv` (first and last years) and the `data_centre_share_of_demand_growth` rows of `published_estimates.csv` |
| Primary key | `jurisdiction` |
| Time coverage | Ireland 2015-2025 (measured); others 2024-2030 (projected) |
| Latest observation | Ireland 2025; others are projections |
| Transform | Ireland: (data centre consumption 2025 - 2015) / ((data centres 2025 - 2015) + (other customers 2025 - 2015)) x 100, rounded to one decimal place. Others: the IEA's published shares, labelled with their qualifier. Sorted by share, highest first. |

Columns as `jurisdiction_share.csv`, with `share_pct` = share of the increase in electricity demand, in
percent, and `basis` = `metered` or `projection`.

### `projections.csv`

| Field | Value |
|---|---|
| Built from | `data_centre_electricity` rows of `published_estimates.csv` |
| Primary key | `jurisdiction`, `year` |
| Time coverage | 2023-2035 |
| Latest observation | Estimates: World 2025, United States 2023. Projections run to 2035. |
| Transform | Groups the TWh figures by jurisdiction and year. The `estimate`, `base case` or `reference case` figure becomes `central_twh`; the lowest and highest cases or bounds become `low_twh` and `high_twh`. Where a publisher gives only a range, `central_twh` is left blank rather than invented. |

| Column | Type | Unit | Description |
|---|---|---|---|
| `jurisdiction` | string | - | `World` or `United States` |
| `year` | integer | year | Year the figure refers to |
| `kind` | string | - | `estimate` (past year) or `projection` |
| `central_twh` | number | TWh per year | Published estimate, base or reference case |
| `low_twh` | number | TWh per year | Lowest published case or bound; blank if none |
| `high_twh` | number | TWh per year | Highest published case or bound; blank if none |
| `source` | string | - | Short citation, naming the report edition |

### `growth_2025.csv`

| Field | Value |
|---|---|
| Built from | `annual_growth_rate` rows of `published_estimates.csv` |
| Primary key | `subject` |
| Time coverage | 2025 against 2024 |
| Latest observation | 2025 |
| Transform | Selects the three growth rates and sorts them, highest first. |

| Column | Type | Unit | Description |
|---|---|---|---|
| `subject` | string | - | `AI-focused data centres`, `All data centres` or `All electricity demand` |
| `year` | integer | year | 2025 |
| `growth_pct` | number | percent | Growth in electricity consumption from 2024 |
| `source` | string | - | Short citation |

### `ai_share.csv`

| Field | Value |
|---|---|
| Built from | `ai_share_of_data_centre_electricity` rows of `published_estimates.csv` |
| Primary key | `jurisdiction`, `year` |
| Time coverage | 2024 |
| Latest observation | 2024 |
| Transform | Combines the low and high estimates into one row. |

| Column | Type | Unit | Description |
|---|---|---|---|
| `jurisdiction` | string | - | `United States` |
| `year` | integer | year | Year of the estimate |
| `low_pct` | number | percent | Low estimate of AI's share of data centre electricity |
| `high_pct` | number | percent | High estimate |
| `source` | string | - | Short citation |

---

## Validation

`src/pipeline.py` stops with an error if any of these fail:

- The annual CSO table covers every year from 2015 to 2025, with no missing or non-positive values.
- For each year, data centres plus other customers equals the published total to within 2 GWh. CSO rounds
  each figure independently; in 2020, 2021 and 2025 the components differ from the total by 1 GWh.
- Each year in the quarterly table has exactly four quarters, and the four quarters sum to the annual data
  centre figure to within 2 GWh. In 2016, 2018, 2019, 2020, 2021, 2022, 2024 and 2025 the quarters differ
  from the annual figure by 1 GWh.
- Every estimate has all required fields, every `estimate_id` is unique, every percentage lies between 0
  and 100, and every TWh value is positive.

## Caveats

- **Data centres, not AI.** Most figures are for all data centres, which also run storage, streaming and
  general cloud services. The AI-specific figures (`growth_2025.csv`'s AI-focused row and `ai_share.csv`)
  are modelled estimates, not meter readings.
- **Two IEA editions.** The 2025 and 2026 IEA reports differ slightly for 2030 (945 TWh against 950 TWh).
  This package uses the 2026 figures where they exist and labels every figure with its edition.
- **Not like-for-like across places.** Ireland's share is metered and uses total metered consumption as the
  denominator. The US and world shares are modelled and use total electricity consumption.
- **CSO identification.** CSO identifies data centres by examining individual meters; a data centre it does
  not identify is counted under other customers.
- **Revisions.** CSO revises earlier years in each release. The 2025 release changed 2024 data centre
  consumption from 6,969 GWh to 6,973 GWh. This package uses the 2025 release throughout.
