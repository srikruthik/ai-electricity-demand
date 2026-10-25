"""Tab 3 chart: AI-specific evidence."""

from __future__ import annotations

import altair as alt
import pandas as pd

from src.style import title as wrap_title, DATA_CENTRES, NEUTRAL, OTHER

def ai_growth(frame: pd.DataFrame) -> alt.Chart:
    """Magnitude: 2025 growth in electricity use, AI-focused data centres against the rest."""
    data = frame.copy()
    data["label"] = data["growth_pct"].map(lambda v: f"+{v:g}%")
    order = data["subject"].tolist()
    bars = alt.Chart(data).mark_bar().encode(
        y=alt.Y("subject:N", sort=order, title="What is measured", axis=alt.Axis(labelLimit=220)),
        x=alt.X("growth_pct:Q", title="Growth in electricity consumption, 2025 (%)",
                scale=alt.Scale(domain=[0, 60])),
        color=alt.Color("subject:N", legend=None, scale=alt.Scale(
            domain=["AI-focused data centres", "All data centres", "All electricity demand"],
            range=[DATA_CENTRES, OTHER, NEUTRAL])),
    )
    labels = alt.Chart(data).mark_text(align="left", dx=6, fontSize=13, fontWeight="bold").encode(
        y=alt.Y("subject:N", sort=order), x="growth_pct:Q", text="label:N"
    )
    return (bars + labels).properties(title=wrap_title("In 2025, AI-focused data centres' electricity use grew about three times as fast as all data centres (%)"),
        height=230,
    )
