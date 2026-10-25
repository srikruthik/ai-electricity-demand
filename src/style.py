"""Shared chart palette. Okabe-Ito colours stay distinguishable under the
common colour vision deficiencies.
"""

import textwrap

import altair as alt

DATA_CENTRES = "#D55E00"
OTHER = "#0072B2"
MODELLED = "#56B4E9"
NEUTRAL = "#666666"

SERIES_SCALE = alt.Scale(
    domain=["Data centres", "All other metered customers"],
    range=[DATA_CENTRES, OTHER],
)


def title(text: str, width: int = 62) -> alt.TitleParams:
    return alt.TitleParams(textwrap.wrap(text, width), anchor="start", fontSize=14)
