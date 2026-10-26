"""Ireland panel shared by Streamlit and the static HTML export."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

TEMPLATE = Path(__file__).with_name("ireland_panel.html")
COLS = ["year", "data_centres_gwh", "other_gwh", "total_gwh",
        "data_centre_share_pct", "dc_change_gwh", "other_change_gwh"]


def render(data: pd.DataFrame, dc: str, other: str) -> str:
    rows = data.sort_values("year")[COLS].copy()
    rows = rows.astype(object).where(pd.notna(rows), None)
    values = json.dumps(rows.to_dict("records"), separators=(",", ":"), allow_nan=False)
    page = TEMPLATE.read_text(encoding="utf-8")
    page = page.replace("/*__IRELAND_DATA__*/", values + " ||")
    page = page.replace("const C={teal:'#18766F',slate:'#8798A5'",
                        f"const C={{teal:'{dc}',slate:'{other}'")
    return page
