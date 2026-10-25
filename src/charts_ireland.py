"""Tab 1 charts: Ireland's metered data centre electricity."""

from __future__ import annotations

import altair as alt
import pandas as pd

from src.style import title as wrap_title, NEUTRAL, SERIES_SCALE

def ireland_trend(annual: pd.DataFrame, indexed: bool) -> alt.Chart:
    """Change over time: data centres against every other metered customer."""
    long = annual.melt(
        id_vars="year",
        value_vars=["data_centres_gwh", "other_gwh"],
        var_name="series",
        value_name="gwh",
    )
    long["series"] = long["series"].map(
        {"data_centres_gwh": "Data centres", "other_gwh": "All other metered customers"}
    )
    first_year = int(annual["year"].min())
    if indexed:
        base = long.loc[long["year"] == first_year].set_index("series")["gwh"]
        long["value"] = (long["gwh"] / long["series"].map(base) * 100).round(0)
        y_title = f"Consumption index ({first_year} = 100)"
        label_format = ",.0f"
        title = f"Data centre consumption grew far faster than everything else (index, {first_year} = 100)"
    else:
        long["value"] = long["gwh"]
        y_title = "Metered electricity consumption (GWh)"
        label_format = ",.0f"
        title = "Metered electricity consumption in Ireland by customer type (GWh)"

    base_chart = alt.Chart(long).encode(
        x=alt.X("year:O", title="Year", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("value:Q", title=y_title, scale=alt.Scale(zero=True)),
        color=alt.Color("series:N", scale=SERIES_SCALE, title="Customer type",
                        legend=alt.Legend(orient="bottom")),
    )
    lines = base_chart.mark_line(point=True, strokeWidth=2.5)
    dc_labels = base_chart.transform_filter(alt.datum.series == "Data centres").mark_text(
        dy=-12, fontSize=11
    ).encode(text=alt.Text("value:Q", format=label_format))
    other_labels = base_chart.transform_filter(
        alt.datum.series == "All other metered customers"
    ).mark_text(dy=14, fontSize=11).encode(text=alt.Text("value:Q", format=label_format))
    return (lines + dc_labels + other_labels).properties(title=wrap_title(title), height=340)


def ireland_share(annual: pd.DataFrame) -> alt.Chart:
    """Part-to-whole: each year's metered total split into its two parts."""
    rows = []
    for record in annual.itertuples(index=False):
        dc = float(record.data_centre_share_pct)
        rows.append({"year": str(record.year), "part": "Data centres", "start": 0.0, "end": dc,
                     "label": f"{dc:.1f}%"})
        rows.append({"year": str(record.year), "part": "All other metered customers",
                     "start": dc, "end": 100.0, "label": f"{100 - dc:.1f}%"})
    frame = pd.DataFrame(rows)
    frame["mid"] = (frame["start"] + frame["end"]) / 2

    bars = alt.Chart(frame).mark_bar().encode(
        y=alt.Y("year:O", title="Year", sort="descending"),
        x=alt.X("start:Q", title="Share of total metered electricity consumption (%)",
                scale=alt.Scale(domain=[0, 100])),
        x2="end:Q",
        color=alt.Color("part:N", scale=SERIES_SCALE, title="Customer type",
                        legend=alt.Legend(orient="bottom")),
    )
    dc_text = alt.Chart(frame.loc[frame["part"] == "Data centres"]).mark_text(
        align="right", dx=-4, fontSize=11, fontWeight="bold", color="white"
    ).encode(y=alt.Y("year:O", sort="descending"), x="end:Q", text="label:N")
    other_text = alt.Chart(frame.loc[frame["part"] != "Data centres"]).mark_text(
        align="right", dx=-6, fontSize=11, fontWeight="bold", color="white"
    ).encode(y=alt.Y("year:O", sort="descending"), x="end:Q", text="label:N")
    return (bars + dc_text + other_text).properties(title=wrap_title("Data centres' share of Ireland's metered electricity, by year (%)"),
        height=36 * len(annual) + 40,
    )


def growth_split(growth: pd.DataFrame, first_year: int, last_year: int) -> alt.Chart:
    """Magnitude: how much each customer type added between two years."""
    frame = growth.copy()
    frame["label"] = frame["change_gwh"].map(lambda v: f"{v:+,.0f} GWh")
    bars = alt.Chart(frame).mark_bar(size=120).encode(
        x=alt.X("series:N", title="Customer type", sort=["Data centres", "All other metered customers"],
                axis=alt.Axis(labelAngle=0)),
        y=alt.Y("change_gwh:Q", title=f"Change in consumption, {first_year}-{last_year} (GWh)",
                scale=alt.Scale(domain=[min(0, frame["change_gwh"].min() * 1.15),
                                        max(0, frame["change_gwh"].max() * 1.15)])),
        color=alt.Color("series:N", scale=SERIES_SCALE, legend=None),
    )
    labels = alt.Chart(frame).transform_calculate(
        label_y="datum.change_gwh >= 0 ? datum.change_gwh : 0"
    ).mark_text(fontSize=13, fontWeight="bold", dy=-10).encode(
        x=alt.X("series:N", sort=["Data centres", "All other metered customers"]),
        y=alt.Y("label_y:Q"),
        text="label:N",
    )
    rule = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color=NEUTRAL).encode(y="y:Q")
    return (bars + rule + labels).properties(title=wrap_title(f"Change in metered consumption by customer type, {first_year} to {last_year} (GWh)"),
        height=320,
    )


def ireland_yoy(annual: pd.DataFrame) -> alt.Chart:
    """Deviation: each year's change in consumption, data centres against everyone else."""
    data = annual.dropna(subset=["dc_change_gwh"]).melt(
        id_vars="year", value_vars=["dc_change_gwh", "other_change_gwh"],
        var_name="series", value_name="change",
    )
    data["series"] = data["series"].map(
        {"dc_change_gwh": "Data centres", "other_change_gwh": "All other metered customers"}
    )
    data["change"] = data["change"].astype(float)
    data["label"] = data["change"].map(lambda v: f"{v:+,.0f}")
    data["label_y"] = data["change"]
    data["dy"] = data["change"].map(lambda v: -8 if v >= 0 else 12)
    lo = min(0.0, data["change"].min() * 1.25)
    hi = max(0.0, data["change"].max() * 1.2)
    base = alt.Chart(data).encode(
        x=alt.X("year:O", title="Year", axis=alt.Axis(labelAngle=0)),
        xOffset=alt.XOffset("series:N", sort=["Data centres", "All other metered customers"]),
    )
    bars = base.mark_bar().encode(
        y=alt.Y("change:Q", title="Change from previous year (GWh)", scale=alt.Scale(domain=[lo, hi])),
        color=alt.Color("series:N", scale=SERIES_SCALE, title="Customer type",
                        legend=alt.Legend(orient="bottom")),
    )
    up = base.transform_filter(alt.datum.change >= 0).mark_text(dy=-7, fontSize=9.5).encode(
        y="label_y:Q", text="label:N")
    down = base.transform_filter(alt.datum.change < 0).mark_text(dy=10, fontSize=9.5).encode(
        y="label_y:Q", text="label:N")
    rule = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color=NEUTRAL).encode(y="y:Q")
    return (bars + rule + up + down).properties(title=wrap_title("Data centre use rose every year; other customers' use swung up and down (GWh)"),
        height=340,
    )
