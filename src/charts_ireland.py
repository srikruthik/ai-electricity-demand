"""Ireland electricity charts. CSO Data Centres Metered Electricity 2025, Table 1."""
from __future__ import annotations

import altair as alt
import pandas as pd

from src.style import title

DC = "Data centres"
OTHER = "All other metered customers"
SERIES = [DC, OTHER]
DC_COLOR = "#18766F"
OTHER_COLOR = "#8798A5"
PALE = "#DDE5E9"
NET_COLOR = "#354D60"
INK = "#293E4C"
GRID = "#E8EDF0"
RULE = "#AEBCC5"
COLORS = alt.Scale(domain=SERIES, range=[DC_COLOR, OTHER_COLOR])


def _axis(year=False):
    opts = dict(labelColor=INK, titleColor=INK, gridColor=GRID,
                tickColor=RULE, domainColor=RULE, labelFontSize=11,
                titleFontSize=11, labelOverlap=True)
    if year:
        opts["labelAngle"] = 0
    return alt.Axis(**opts)


def _pct(a, b):
    return 100 * (b / a - 1)


def _start_end(df):
    df = df.sort_values("year")
    return df.iloc[0], df.iloc[-1]


def ireland_trend(annual: pd.DataFrame, indexed: bool) -> alt.LayerChart:
    df = annual.sort_values("year").copy()
    a, b = _start_end(df)
    year = int(a["year"])
    data = df.melt(id_vars="year", value_vars=["data_centres_gwh", "other_gwh"],
                   var_name="col", value_name="gwh")
    data["series"] = data["col"].map({"data_centres_gwh": DC, "other_gwh": OTHER})
    base = {DC: a["data_centres_gwh"], OTHER: a["other_gwh"]}
    data["index"] = 100 * data["gwh"] / data["series"].map(base)
    data["growth"] = data["index"] - 100
    data["value"] = data["index"] if indexed else data["gwh"]
    data["label"] = data["value"].map(lambda v: f"{v:,.0f}")

    x = alt.X("year:O", sort="ascending", title=None, axis=_axis(year=True))
    y = alt.Y("value:Q", title=f"Index ({year} = 100)" if indexed else "Annual electricity (GWh)",
              scale=alt.Scale(zero=True), axis=_axis())
    chart = alt.Chart(data).encode(
        x=x, y=y,
        color=alt.Color("series:N", scale=COLORS, title=None,
                        legend=alt.Legend(orient="bottom", labelFontSize=11)),
        tooltip=[alt.Tooltip("year:O", title="Year"),
                 alt.Tooltip("series:N", title="Customer group"),
                 alt.Tooltip("gwh:Q", title="Electricity (GWh)", format=",.0f"),
                 alt.Tooltip("index:Q", title=f"Index ({year} = 100)", format=",.1f"),
                 alt.Tooltip("growth:Q", title="Growth from start (%)", format="+.1f")],
    )
    end = data[data["year"] == int(b["year"])]
    labels = []
    for name, color, dy in [(DC, DC_COLOR, -14), (OTHER, OTHER_COLOR, 13)]:
        labels.append(
            alt.Chart(end[end["series"] == name]).mark_text(
                align="right", dx=-8, dy=dy, color=color, fontSize=12,
                fontWeight="bold",
            ).encode(x=x, y=y, text="label:N")
        )
    a_dc, b_dc = int(a["data_centres_gwh"]), int(b["data_centres_gwh"])
    a_other, b_other = int(a["other_gwh"]), int(b["other_gwh"])
    msg = (f"01 | Data-centre use {_pct(a_dc, b_dc):+.0f}%; "
           f"other customers {_pct(a_other, b_other):+.1f}%")
    return (chart.mark_line(point=True, strokeWidth=2.7) + labels[0] + labels[1]).properties(
        title=title(msg, width=85), height=280,
    )


def ireland_share(annual: pd.DataFrame) -> alt.LayerChart:
    a, b = _start_end(annual)
    years = [str(int(a["year"])), str(int(b["year"]))]
    rows = []
    for r in [a, b]:
        p = float(r["data_centre_share_pct"])
        val = {"year": str(int(r["year"])), "dc_gwh": int(r["data_centres_gwh"]),
               "total_gwh": int(r["total_gwh"])}
        rows.extend([{**val, "series": DC, "low": 0, "high": p, "pct": p},
                     {**val, "series": OTHER, "low": p, "high": 100, "pct": 100-p}])
    df = pd.DataFrame(rows)
    end = df[df["series"] == DC].copy()
    end["label"] = end["pct"].map(lambda p: f"{p:.1f}%")
    end["pos"] = 102.0
    scale = alt.Scale(domain=[0, 116], nice=False)
    y = alt.Y("year:N", sort=years, title=None,
              axis=alt.Axis(labelColor=INK, labelFontSize=12, labelFontWeight="bold",
                            domain=False, ticks=False))
    x = alt.X("low:Q", title="Share of metered electricity (%)", scale=scale,
              axis=alt.Axis(values=[0, 25, 50, 75, 100],
                            labelColor=INK, titleColor=INK, gridColor=GRID))
    bars = alt.Chart(df).mark_bar(size=43, cornerRadiusEnd=3).encode(
        x=x, x2="high:Q", y=y,
        color=alt.Color("series:N", title=None,
                        scale=alt.Scale(domain=SERIES, range=[DC_COLOR, PALE]),
                        legend=alt.Legend(orient="bottom", labelFontSize=11)),
        tooltip=[alt.Tooltip("year:N", title="Year"),
                 alt.Tooltip("series:N", title="Customer group"),
                 alt.Tooltip("pct:Q", title="Share (%)", format=".1f"),
                 alt.Tooltip("dc_gwh:Q", title="Data centres (GWh)", format=",.0f"),
                 alt.Tooltip("total_gwh:Q", title="Total (GWh)", format=",.0f")],
    )
    labels = alt.Chart(end).mark_text(
        align="left", dx=3, color=DC_COLOR, fontSize=12, fontWeight="bold",
    ).encode(x=alt.X("pos:Q", scale=scale), y=y, text="label:N")
    msg = (f"02 | Data-centre share rose from {a['data_centre_share_pct']:.1f}% "
           f"to {b['data_centre_share_pct']:.1f}%")
    return (bars + labels).properties(title=title(msg, width=85), height=148)


def growth_split(growth: pd.DataFrame, first_year: int, last_year: int) -> alt.LayerChart:
    change = growth.set_index("series")["change_gwh"]
    dc, other = int(change[DC]), int(change[OTHER])
    net = dc + other
    df = pd.DataFrame([
        {"step": "Data centres", "a": 0, "b": dc, "change": dc, "group": DC},
        {"step": "Other customers", "a": dc, "b": net, "change": other, "group": OTHER},
        {"step": "Net change", "a": 0, "b": net, "change": net, "group": "Net change"},
    ])
    df["low"] = df[["a", "b"]].min(axis=1)
    df["high"] = df[["a", "b"]].max(axis=1)
    df["label"] = df["change"].map(lambda v: f"{v:+,}")
    top = max(100.0, float(df[["low", "high"]].abs().max().max()))
    lo = min(-.1 * top, float(df["low"].min()) - .3 * top)
    hi = max(.1 * top, float(df["high"].max()) + .15 * top)
    scale = alt.Scale(domain=[lo, hi], nice=False)
    x = alt.X("step:N", title=None,
              sort=["Data centres", "Other customers", "Net change"],
              axis=alt.Axis(labelColor=INK, domain=False, ticks=False,
                            labelFontSize=11, labelLimit=145))
    y = alt.Y("high:Q", scale=scale, title="Change in annual use (GWh)", axis=_axis())
    ends = alt.Y("b:Q", scale=scale)
    bars = alt.Chart(df).mark_bar(size=72).encode(
        x=x, y=y, y2="low:Q",
        color=alt.Color("group:N", legend=None,
                        scale=alt.Scale(domain=[DC, OTHER, "Net change"],
                                        range=[DC_COLOR, OTHER_COLOR, NET_COLOR])),
        tooltip=[alt.Tooltip("step:N", title="Component"),
                 alt.Tooltip("change:Q", title="Change (GWh)", format="+,.0f")],
    )
    zero = alt.Chart(pd.DataFrame({"zero": [0]})).mark_rule(color=RULE).encode(
        y=alt.Y("zero:Q", scale=scale))
    up = alt.Chart(df[df["change"] >= 0]).mark_text(
        dy=-14, color=INK, fontSize=12, fontWeight="bold",
    ).encode(x=x, y=ends, text="label:N")
    down = alt.Chart(df[df["change"] < 0]).mark_text(
        dy=17, color=INK, fontSize=12, fontWeight="bold",
    ).encode(x=x, y=ends, text="label:N")
    if net > 0:
        msg = f"03 | Data centres contributed {100*dc/net:.1f}% of net demand growth"
    elif net < 0:
        msg = f"03 | Total metered use fell {abs(net):,} GWh despite data-centre growth"
    else:
        msg = "03 | No net demand growth in the selected years"
    return (bars + zero + up + down).properties(title=title(msg, width=85), height=265)


def ireland_yoy(annual: pd.DataFrame) -> alt.LayerChart:
    df = annual.dropna(subset=["dc_change_gwh", "other_change_gwh"]).sort_values("year")
    if df.empty:
        raise ValueError("Select at least one year of annual changes.")
    a = df[["year", "dc_change_gwh", "data_centres_gwh"]].copy()
    a["change"] = a["dc_change_gwh"]
    a["prev"] = a["data_centres_gwh"] - a["change"]
    a["series"] = DC
    b = df[["year", "other_change_gwh", "other_gwh"]].copy()
    b["change"] = b["other_change_gwh"]
    b["prev"] = b["other_gwh"] - b["change"]
    b["series"] = OTHER
    data = pd.concat([a[["year", "change", "prev", "series"]],
                      b[["year", "change", "prev", "series"]]], ignore_index=True)
    data["rate"] = 100 * data["change"] / data["prev"]
    data["label"] = data["change"].map(lambda v: f"{v:+,.0f}")
    lead = set(df.loc[df["other_change_gwh"] > df["dc_change_gwh"], "year"].astype(int))
    peak = int(df.loc[df["dc_change_gwh"].idxmax(), "year"])
    last = int(df.iloc[-1]["year"])
    mark = data[((data["series"] == DC) & data["year"].isin([peak, last])) |
                ((data["series"] == OTHER) &
                 (data["year"].isin(lead) | (data["change"] < 0)))]
    lo = min(0.0, float(data["change"].min()) * 1.4)
    hi = max(0.0, float(data["change"].max()) * 1.3)
    x = alt.X("year:O", title=None, sort="ascending", axis=_axis(year=True))
    off = alt.XOffset("series:N", sort=SERIES)
    y = alt.Y("change:Q", title="Change from previous year (GWh)",
              scale=alt.Scale(domain=[lo, hi], nice=False), axis=_axis())
    bars = alt.Chart(data).mark_bar().encode(
        x=x, xOffset=off, y=y,
        color=alt.Color("series:N", scale=COLORS, title=None,
                        legend=alt.Legend(orient="bottom", labelFontSize=11)),
        tooltip=[alt.Tooltip("year:O", title="Year"),
                 alt.Tooltip("series:N", title="Customer group"),
                 alt.Tooltip("change:Q", title="Annual change (GWh)", format="+,.0f"),
                 alt.Tooltip("rate:Q", title="YoY growth (%)", format="+.1f")],
    )
    up = alt.Chart(mark[mark["change"] >= 0]).mark_text(
        dy=-10, color=INK, fontSize=10, fontWeight="bold",
    ).encode(x=x, xOffset=off, y=y, text="label:N")
    down = alt.Chart(mark[mark["change"] < 0]).mark_text(
        dy=14, color=INK, fontSize=10, fontWeight="bold",
    ).encode(x=x, xOffset=off, y=y, text="label:N")
    zero = alt.Chart(pd.DataFrame({"zero": [0]})).mark_rule(color=RULE).encode(y="zero:Q")
    if len(df) == 1:
        msg = f"04 | In {last}, data centres added {int(df.iloc[-1]['dc_change_gwh']):+,} GWh"
    elif lead:
        msg = f"04 | Other customers added more in {len(lead)} of {len(df)} years"
    else:
        msg = "04 | Data centres added more in every selected year"
    return (bars + zero + up + down).properties(title=title(msg, width=85), height=300)


def ireland_panel(annual: pd.DataFrame) -> str:
    from src.ireland_panel import render
    return render(annual, DC_COLOR, OTHER_COLOR)
