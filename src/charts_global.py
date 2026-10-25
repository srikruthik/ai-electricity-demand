"""Tab 2 charts: Ireland against the US, other economies and the world."""

from __future__ import annotations

import altair as alt
import pandas as pd

from src.style import title as wrap_title, DATA_CENTRES, MODELLED, OTHER

def comparison(frame: pd.DataFrame, lens: str, complete: bool = True) -> alt.Chart:
    """Ranking: data centre significance by place, measured one of two ways."""
    data = frame.copy()
    data["text"] = data.apply(lambda r: f"{r.label} ({r.basis}, {r.period})", axis=1)
    order = data.sort_values("share_pct", ascending=False)["jurisdiction"].tolist()
    if lens == "use":
        x_title = "Data centre share of electricity consumption (%)"
        title = ("Share of electricity use: Ireland stands far above the US and the world (%)" if complete
                 else "Data centre share of electricity use, selected places (%)")
    else:
        x_title = "Data centres' share of growth in electricity demand (%)"
        title = ("Share of demand growth: data centres matter far more for growth than for use (%)" if complete
                 else "Data centres' share of growth in electricity demand, selected places (%)")
    domain_max = max(36.0, float(data["share_pct"].max()) * 1.45)
    palette = {"metered": DATA_CENTRES, "modelled": MODELLED, "projection": "#999999"}
    present = [b for b in palette if b in set(data["basis"])]
    bars = alt.Chart(data).mark_bar().encode(
        y=alt.Y("jurisdiction:N", sort=order, title="Place", axis=alt.Axis(labelLimit=220)),
        x=alt.X("share_pct:Q", title=x_title, scale=alt.Scale(domain=[0, domain_max])),
        color=alt.Color("basis:N", title="How it was measured",
                        scale=alt.Scale(domain=present, range=[palette[b] for b in present]),
                        legend=alt.Legend(orient="bottom")),
    )
    labels = alt.Chart(data).mark_text(align="left", dx=5, fontSize=12).encode(
        y=alt.Y("jurisdiction:N", sort=order), x="share_pct:Q", text="text:N"
    )
    return (bars + labels).properties(title=wrap_title(title), height=max(170, 58 * len(data) + 40))


def projections(frame: pd.DataFrame, jurisdiction: str) -> alt.Chart:
    """Change over time: published estimates and the projected range."""
    data = frame.copy()

    def label(r: pd.Series) -> str:
        if pd.notna(r.central_twh) and pd.notna(r.low_twh):
            return f"{r.central_twh:,.0f} TWh, range {r.low_twh:,.0f}-{r.high_twh:,.0f} ({r.source})"
        if pd.notna(r.central_twh):
            return f"{r.central_twh:,.0f} TWh ({r.source})"
        return f"{r.low_twh:,.0f}-{r.high_twh:,.0f} TWh ({r.source})"

    data["label"] = data.apply(label, axis=1)
    data = data.sort_values("year").reset_index(drop=True)
    top = data[["central_twh", "high_twh"]].max(axis=1)
    bottom = data[["central_twh", "low_twh"]].min(axis=1)
    pad = float(top.max()) * 0.06
    crowded = data["year"].shift(-1).sub(data["year"]).le(2).fillna(False)
    data["label_y"] = (bottom - pad * 1.6).where(crowded, top + pad * 0.2)
    data["point_y"] = data["central_twh"]
    years = data["year"]
    year_axis = alt.X("year:Q", title="Year",
                      scale=alt.Scale(domain=[int(years.min()) - 2, int(years.max()) + 3]),
                      axis=alt.Axis(format="d", values=sorted(years.unique().tolist()), labelAngle=0))
    y_title = "Data centre electricity consumption (TWh per year)"

    y_scale = alt.Scale(domain=[0, float(top.max()) * 1.2])

    ranges = alt.Chart(data.dropna(subset=["low_twh"])).mark_rule(
        strokeWidth=10, opacity=0.35, color=OTHER
    ).encode(x=year_axis, y=alt.Y("low_twh:Q", title=y_title, scale=y_scale),
             y2="high_twh:Q")
    points = alt.Chart(data.dropna(subset=["point_y"])).mark_point(
        filled=True, size=110, color=OTHER
    ).encode(x=year_axis, y=alt.Y("point_y:Q", title=y_title, scale=y_scale),
             shape=alt.Shape("kind:N", title="Figure type",
                             scale=alt.Scale(domain=["estimate", "projection"],
                                             range=["circle", "triangle-up"]),
                             legend=alt.Legend(orient="bottom")))
    labels = alt.Chart(data).mark_text(dy=-8, fontSize=11).encode(
        x=year_axis, y=alt.Y("label_y:Q", title=y_title, scale=y_scale), text="label:N"
    )
    return (ranges + points + labels).properties(title=wrap_title(f"{jurisdiction}: data centre electricity is projected to keep rising (TWh per year)"),
        height=340,
    )
