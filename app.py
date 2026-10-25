from __future__ import annotations

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from src import charts_ai, charts_global, charts_ireland

ROOT = Path(__file__).resolve().parent
PROCESSED = ROOT / "data" / "processed"
LAST_REFRESH = "2026-10-20"
QUESTION = "Is AI becoming a significant driver of electricity demand?"

st.set_page_config(page_title="AI and electricity demand", page_icon="⚡", layout="centered")


@st.cache_data
def load() -> dict[str, pd.DataFrame]:
    return {
        name: pd.read_csv(PROCESSED / f"{name}.csv")
        for name in ["ireland_annual", "jurisdiction_share", "growth_share", "projections",
                     "growth_2025", "ai_share"]
    }


def show(chart: alt.Chart) -> None:
    heading = chart.title
    if heading is not alt.Undefined:
        text = heading.text if isinstance(heading, alt.TitleParams) else heading
        st.markdown(f"**{' '.join(text) if isinstance(text, list) else text}**")
        chart = chart.properties(title="")
    chart = chart.properties(autosize=alt.AutoSizeParams(type="fit-x", contains="padding"))
    st.altair_chart(chart, width="stretch", theme=None)


def growth_between(ireland: pd.DataFrame, first: int, last: int) -> pd.DataFrame:
    start = ireland.loc[ireland["year"] == first].iloc[0]
    end = ireland.loc[ireland["year"] == last].iloc[0]
    return pd.DataFrame({
        "series": ["Data centres", "All other metered customers"],
        "change_gwh": [int(end["data_centres_gwh"] - start["data_centres_gwh"]),
                       int(end["other_gwh"] - start["other_gwh"])],
    })


data = load()
ireland = data["ireland_annual"]
use_share = data["jurisdiction_share"]
growth_share = data["growth_share"]
proj = data["projections"]
rates = data["growth_2025"].set_index("subject")["growth_pct"]
ai = data["ai_share"].iloc[0]

first_year, last_year = int(ireland["year"].min()), int(ireland["year"].max())
start_row, end_row = ireland.iloc[0], ireland.iloc[-1]
dc_full = int(end_row["data_centres_gwh"] - start_row["data_centres_gwh"])
other_full = int(end_row["other_gwh"] - start_row["other_gwh"])
growth_pct = float(growth_share.loc[growth_share["jurisdiction"] == "Ireland", "share_pct"].iloc[0])
share_start = float(start_row["data_centre_share_pct"])
share_end = float(end_row["data_centre_share_pct"])
world_use = use_share.loc[use_share["jurisdiction"] == "World"].iloc[0]
world_growth = growth_share.loc[growth_share["jurisdiction"] == "World"].iloc[0]
adv_growth = growth_share.loc[growth_share["jurisdiction"] == "Advanced economies"].iloc[0]
us_growth = growth_share.loc[growth_share["jurisdiction"] == "United States"].iloc[0]
ai_rate = rates["AI-focused data centres"]
dc_rate = rates["All data centres"]
all_rate = rates["All electricity demand"]

st.title(QUESTION)
st.caption(
    f"Data last refreshed {LAST_REFRESH} · Ireland: Central Statistics Office, 7 July 2026 release "
    "(metered, 2015-2025) · World: International Energy Agency, 2025 and 2026 reports · "
    "United States: Lawrence Berkeley National Laboratory, 2024 report and 2025 update"
)

st.subheader(
    f"Data centres supplied {growth_pct:.0f}% of the growth in Ireland's metered electricity demand "
    f"from {first_year} to {last_year}."
)
m1, m2, m3, m4 = st.columns(4)
m1.metric(f"Ireland data centre share, {last_year}", f"{share_end:.1f}%",
          f"{share_end - share_start:+.1f} pts since {first_year}")
m2.metric(f"Ireland share of demand growth, {first_year}-{last_year}", f"{growth_pct:.0f}%")
m3.metric("Growth of AI-focused data centres, 2025", f"+{ai_rate:.0f}%",
          help="IEA modelled estimate, global.")
m4.metric(f"World data centre share, {world_use['period']}", f"{world_use['share_pct']:.1f}%",
          help="IEA modelled estimate of share of global electricity consumption.")

with st.expander(f"How the {growth_pct:.0f}% is calculated"):
    st.markdown(
        f"From `data/processed/ireland_annual.csv`, built from CSO Table 1 "
        f"(`data/source/cso_mec02_annual.csv`):\n\n"
        f"| | {first_year} | {last_year} | Change |\n|---|---:|---:|---:|\n"
        f"| Data centres (GWh) | {int(start_row['data_centres_gwh']):,} | {int(end_row['data_centres_gwh']):,} | {dc_full:+,} |\n"
        f"| All other metered customers (GWh) | {int(start_row['other_gwh']):,} | {int(end_row['other_gwh']):,} | {other_full:+,} |\n\n"
        f"Data centres' share of the increase = {dc_full:,} / ({dc_full:,} + {other_full:,}) "
        f"= **{growth_pct:.1f}%**."
    )

st.markdown("#### The answer")
st.success(
    f"**Locally, yes. Globally, not yet, though it is heading that way. And AI is the fastest-growing "
    f"part.** In Ireland, where data centre use is metered, data centres rose from {share_start:.1f}% to "
    f"{share_end:.1f}% of electricity use between {first_year} and {last_year} and supplied "
    f"{growth_pct:.0f}% of all growth in demand. Worldwide they used {world_use['label']} of electricity in "
    f"{world_use['period']}, but the IEA projects they will supply {world_growth['label']} of global demand "
    f"growth to 2030, {adv_growth['label']} in advanced economies and {us_growth['label']} in the United "
    f"States. In 2025, AI-focused data centres' electricity use grew {ai_rate:.0f}%, against "
    f"{dc_rate:.0f}% for all data centres and {all_rate:.0f}% for all electricity demand. How much of total "
    f"data centre electricity AI uses is estimated, not measured."
)
st.caption(
    "Who this is for: a demand-forecasting analyst at a national electricity system operator, deciding "
    "whether data centre load needs its own growth category in the next long-term demand forecast."
)

tab1, tab2, tab3 = st.tabs(["1. Ireland: what meters show", "2. Is Ireland an outlier?",
                            "3. Is it AI specifically?"])

with tab1:
    st.write(
        "Ireland is one of the few countries that measures data centre electricity directly from meters, "
        "which makes it the clearest test case available."
    )
    start_year, end_year = st.slider(
        "Years to compare", min_value=first_year, max_value=last_year,
        value=(first_year, last_year), step=1, key="year_range",
    )
    window = ireland.loc[ireland["year"].between(start_year, end_year)]

    if start_year == end_year:
        st.info("Choose two different years on the slider to compare change over time.")
    else:
        measure = st.radio("Show consumption as", ["Gigawatt hours", f"Index ({start_year} = 100)"],
                           horizontal=True, key="trend_measure")
        show(charts_ireland.ireland_trend(window, indexed=measure != "Gigawatt hours"))
        st.caption(
            f"Annual metered electricity consumption in Ireland, {start_year}-{end_year}, in gigawatt hours "
            f"(GWh). The index sets each customer type's {start_year} value to 100, so growth rates can be "
            "compared despite very different sizes."
        )

        show(charts_ireland.ireland_share(window))
        st.caption(
            f"Each bar is one year's total metered electricity consumption, {start_year}-{end_year}, split "
            "between data centres and every other metered customer, in percent."
        )

        growth = growth_between(ireland, start_year, end_year)
        dc_change, other_change = growth["change_gwh"].tolist()
        show(charts_ireland.growth_split(growth, start_year, end_year))
        net = dc_change + other_change
        if net > 0 and other_change >= 0:
            note = f"Data centres account for {dc_change / net * 100:.0f}% of the net increase of {net:,} GWh."
        elif net > 0:
            note = (f"Consumption by other customers fell, so data centres account for more than the whole "
                    f"net increase of {net:,} GWh.")
        else:
            note = "Total metered consumption did not rise over this period, so a share of growth is not meaningful."
        st.caption(f"Change in annual metered consumption between {start_year} and {end_year}, in GWh. {note}")

        yoy_window = ireland.loc[ireland["year"].between(start_year + 1, end_year)]
        show(charts_ireland.ireland_yoy(yoy_window))
        st.caption(
            f"Change in annual metered consumption from the previous year, {start_year + 1}-{end_year}, in GWh. "
            "Bars above zero are increases; bars below are decreases."
        )

        st.download_button(
            "Download these years as CSV",
            data=window.to_csv(index=False).encode("utf-8"),
            file_name=f"ireland_metered_{start_year}_{end_year}.csv",
            mime="text/csv",
            key="download_ireland",
        )

with tab2:
    lens = st.radio(
        "Measure significance as",
        ["Share of electricity use", "Share of growth in demand"],
        horizontal=True,
        key="lens",
        help="The same data can answer the question differently depending on which you choose.",
    )
    frame = use_share if lens == "Share of electricity use" else growth_share
    lens_key = "use" if lens == "Share of electricity use" else "growth"
    selected = st.multiselect(
        "Places to compare", frame["jurisdiction"].tolist(), default=frame["jurisdiction"].tolist(),
        key=f"jurisdictions_{lens_key}",
    )
    chosen = frame.loc[frame["jurisdiction"].isin(selected)]
    if chosen.empty:
        st.info("No places selected. Choose at least one above to compare.")
    else:
        show(charts_global.comparison(chosen, lens_key, complete=len(chosen) == len(frame)))
        if lens_key == "use":
            st.caption(
                "Data centre share of electricity consumption, in percent. Not like-for-like: Ireland is "
                "metered consumption in 2025 as a share of metered electricity; the United States (2023) and "
                "the world (2024) are modelled estimates as a share of all electricity consumption."
            )
        else:
            st.caption(
                "Data centres' share of the increase in electricity demand, in percent. Not like-for-like: "
                "Ireland is measured growth over 2015-2025; the others are IEA projections for 2024-2030, "
                "published as approximate values ('around', 'more than', 'nearly'), drawn here at the stated value."
            )

    place = st.selectbox("Projections for", sorted(proj["jurisdiction"].unique(), reverse=True),
                         key="projection_place")
    show(charts_global.projections(proj.loc[proj["jurisdiction"] == place], place))
    st.caption(
        "Data centre electricity consumption in terawatt hours (TWh) per year. Circles are published "
        "estimates for past years; triangles are projections, with shaded bars showing the published range "
        "across scenarios. Each label names the report and year it comes from. Projections are scenarios, "
        "not measurements."
    )

with tab3:
    st.write(
        "No public source measures AI's own electricity use. The closest evidence is the IEA's estimate of "
        "consumption by data centres built mainly for AI."
    )
    show(charts_ai.ai_growth(data["growth_2025"]))
    st.caption(
        "Growth in electricity consumption in 2025 compared with 2024, in percent, worldwide. All three are "
        "IEA modelled estimates from Key Questions on Energy and AI (2026) and its press release."
    )
    st.info(
        f"**Growth is not size.** AI-focused data centres grew fastest in 2025, but AI is estimated to use "
        f"only {ai['low_pct']:.0f}-{ai['high_pct']:.0f}% of US data centre electricity ({int(ai['year'])}, "
        f"{ai['source']}). AI is becoming a larger driver of data centre demand; it is not yet most of it."
    )

st.divider()
st.header("What these data cannot show")
st.markdown(
    """
- **AI's measured electricity use.** No source here meters AI. CSO, IEA and LBNL measure or model data
  centres, which also run storage, streaming and cloud services. The AI-specific figures are modelled
  estimates of data centres built mainly for AI, or of AI's share, not meter readings.
- **Why Ireland's consumption rose.** The CSO data record how much electricity data centres used, not
  what ran on them, so they cannot attribute Ireland's growth to AI rather than other cloud services.
- **Whether Ireland is typical.** Ireland is unusually concentrated. Its share is not a forecast for any
  other grid.
- **Exact comparisons across places.** Ireland's figures are metered; the US and world figures are
  modelled or projected, cover different years and use different totals as the denominator.
- **The future.** IEA and LBNL projections are scenarios with wide ranges, and both publishers revised
  their projections between editions. Each figure here is labelled with the report it comes from.
- **Complete coverage in Ireland.** CSO identifies data centres meter by meter; one it misses would be
  counted under other customers.
"""
)

st.divider()
st.header("Sources")
st.markdown(
    f"""
Data last refreshed: **{LAST_REFRESH}**

- **Central Statistics Office (Ireland)**, *Data Centres Metered Electricity Consumption 2025*, released
  7 July 2026, Tables 1 and 2. Metered, 2015-2025. CC BY 4.0.
  [cso.ie](https://www.cso.ie/en/releasesandpublications/ep/p-dcmec/datacentresmeteredelectricityconsumption2025/keyfindings/)
- **International Energy Agency**, *Energy and AI* (April 2025). CC BY 4.0.
  [iea.org](https://www.iea.org/reports/energy-and-ai/executive-summary)
- **International Energy Agency**, *Key Questions on Energy and AI* (16 April 2026) and press release.
  CC BY 4.0. [iea.org](https://www.iea.org/reports/key-questions-on-energy-and-ai/executive-summary)
- **Lawrence Berkeley National Laboratory**, *2024 United States Data Center Energy Usage Report*.
  [lbl.gov](https://energyanalysis.lbl.gov/news/berkeley-lab-report-evaluates-increase-electricity-demand-data-centers)
- **Lawrence Berkeley National Laboratory**, *United States Data Center Energy Usage Report: 2025 Update*
  (June 2026). [lbl.gov](https://eta-publications.lbl.gov/publications/united-states-data-center-energy-2025)
- **Congressional Research Service**, *Data Centers and Their Energy Consumption: Frequently Asked
  Questions* (R48646), citing EPRI.
  [congress.gov](https://www.congress.gov/crs_external_products/R/PDF/R48646/R48646.3.pdf)
"""
)
