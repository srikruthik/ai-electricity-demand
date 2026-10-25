"""Regenerate every processed file in data/processed from data/source.

Run from the repository root:

    python -m src.pipeline           # rebuild data/processed
    python -m src.pipeline --check   # rebuild to a temp folder and compare

Each transform is documented in data/DATA_DICTIONARY.md.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "source"
PROCESSED = ROOT / "data" / "processed"

# CSO rounds each published figure independently, so components and totals
# can disagree by a gigawatt hour or two.
ROUNDING_TOLERANCE_GWH = 2

FIRST_YEAR = 2015
LAST_YEAR = 2025


def load_sources() -> dict[str, pd.DataFrame]:
    return {
        "annual": pd.read_csv(SOURCE / "cso_mec02_annual.csv"),
        "quarterly": pd.read_csv(SOURCE / "cso_mec02_quarterly.csv"),
        "estimates": pd.read_csv(SOURCE / "published_estimates.csv"),
    }


def validate_sources(src: dict[str, pd.DataFrame]) -> None:
    annual = src["annual"]
    quarterly = src["quarterly"]
    estimates = src["estimates"]

    expected_years = list(range(FIRST_YEAR, LAST_YEAR + 1))
    if annual["year"].tolist() != expected_years:
        raise ValueError(f"Annual CSO table must cover {FIRST_YEAR}-{LAST_YEAR} with no gaps")
    if annual.isna().any().any() or (annual.drop(columns="year") <= 0).any().any():
        raise ValueError("Annual CSO table has missing or non-positive values")

    component_gap = (
        annual["data_centres_gwh"] + annual["other_metered_customers_gwh"] - annual["total_gwh"]
    ).abs()
    if (component_gap > ROUNDING_TOLERANCE_GWH).any():
        bad = annual.loc[component_gap > ROUNDING_TOLERANCE_GWH, "year"].tolist()
        raise ValueError(f"Components do not sum to total within rounding for years {bad}")

    if sorted(quarterly["year"].unique().tolist()) != expected_years:
        raise ValueError(f"Quarterly CSO table must cover {FIRST_YEAR}-{LAST_YEAR} with no gaps")
    if quarterly.duplicated(["year", "quarter"]).any():
        raise ValueError("Duplicate year-quarter rows in quarterly CSO table")
    if quarterly.groupby("year")["quarter"].nunique().ne(4).any():
        raise ValueError("Every year in the quarterly CSO table needs four quarters")
    quarter_sums = quarterly.groupby("year")["data_centres_gwh"].sum()
    annual_dc = annual.set_index("year")["data_centres_gwh"]
    quarter_gap = (quarter_sums - annual_dc).abs()
    if (quarter_gap > ROUNDING_TOLERANCE_GWH).any():
        bad = quarter_gap[quarter_gap > ROUNDING_TOLERANCE_GWH].index.tolist()
        raise ValueError(f"Quarterly sums disagree with the annual table for years {bad}")

    required = ["estimate_id", "jurisdiction", "subject", "year", "metric", "value", "unit", "case",
                "method", "source_short", "publisher", "publication", "url"]
    if estimates[required].isna().any().any():
        raise ValueError("A published estimate is missing a required field")
    if estimates["estimate_id"].duplicated().any():
        raise ValueError("Duplicate estimate_id in published estimates")
    shares = estimates.loc[estimates["unit"] == "percent", "value"]
    if not shares.between(0, 100).all():
        raise ValueError("A published percentage lies outside 0-100")
    if (estimates.loc[estimates["unit"] == "TWh", "value"] <= 0).any():
        raise ValueError("A published TWh value is not positive")


def build_ireland_annual(annual: pd.DataFrame) -> pd.DataFrame:
    out = annual.rename(columns={"other_metered_customers_gwh": "other_gwh"}).copy()
    out["data_centre_share_pct"] = (out["data_centres_gwh"] / out["total_gwh"] * 100).round(1)
    out["dc_change_gwh"] = out["data_centres_gwh"].diff().astype("Int64")
    out["other_change_gwh"] = out["other_gwh"].diff().astype("Int64")
    return out[["year", "data_centres_gwh", "other_gwh", "total_gwh", "data_centre_share_pct",
                "dc_change_gwh", "other_change_gwh"]]


def _label(value: float, qualifier) -> str:
    text = f"{value:g}%"
    return f"{qualifier} {text}" if isinstance(qualifier, str) and qualifier else text


def build_jurisdiction_share(ireland: pd.DataFrame, estimates: pd.DataFrame) -> pd.DataFrame:
    latest = ireland.iloc[-1]
    rows = [{
        "jurisdiction": "Ireland",
        "period": str(int(latest["year"])),
        "share_pct": float(latest["data_centre_share_pct"]),
        "label": f"{latest['data_centre_share_pct']:.1f}%",
        "basis": "metered",
        "source": "CSO (2026)",
    }]
    shares = estimates.loc[estimates["metric"] == "data_centre_share_of_electricity"]
    for r in shares.itertuples(index=False):
        rows.append({
            "jurisdiction": r.jurisdiction,
            "period": str(int(r.year)),
            "share_pct": float(r.value),
            "label": _label(r.value, r.qualifier),
            "basis": r.method,
            "source": r.source_short,
        })
    return pd.DataFrame(rows).sort_values("share_pct", ascending=False).reset_index(drop=True)


def build_growth_share(ireland: pd.DataFrame, estimates: pd.DataFrame) -> pd.DataFrame:
    first, last = ireland.iloc[0], ireland.iloc[-1]
    dc = last["data_centres_gwh"] - first["data_centres_gwh"]
    other = last["other_gwh"] - first["other_gwh"]
    share = round(dc / (dc + other) * 100, 1)
    rows = [{
        "jurisdiction": "Ireland",
        "period": f"{int(first['year'])}-{int(last['year'])}",
        "share_pct": share,
        "label": f"{share:.1f}%",
        "basis": "metered",
        "source": "CSO (2026)",
    }]
    growth = estimates.loc[estimates["metric"] == "data_centre_share_of_demand_growth"]
    for r in growth.itertuples(index=False):
        rows.append({
            "jurisdiction": r.jurisdiction,
            "period": f"2024-{int(r.year)}",
            "share_pct": float(r.value),
            "label": _label(r.value, r.qualifier),
            "basis": r.method,
            "source": r.source_short,
        })
    return pd.DataFrame(rows).sort_values("share_pct", ascending=False).reset_index(drop=True)


def build_projections(estimates: pd.DataFrame) -> pd.DataFrame:
    twh = estimates.loc[estimates["metric"] == "data_centre_electricity"]
    central_cases = ("estimate", "base case", "reference case")
    low_cases = ("lowest case", "low bound")
    high_cases = ("highest case", "high bound")
    rows = []
    for (jurisdiction, year), group in twh.groupby(["jurisdiction", "year"]):
        by_case = dict(zip(group["case"], group["value"]))
        rows.append({
            "jurisdiction": jurisdiction,
            "year": int(year),
            "kind": "estimate" if "estimate" in by_case else "projection",
            "central_twh": next((by_case[c] for c in central_cases if c in by_case), None),
            "low_twh": next((by_case[c] for c in low_cases if c in by_case), None),
            "high_twh": next((by_case[c] for c in high_cases if c in by_case), None),
            "source": group["source_short"].iloc[0],
        })
    return pd.DataFrame(rows).sort_values(["jurisdiction", "year"]).reset_index(drop=True)


def build_growth_2025(estimates: pd.DataFrame) -> pd.DataFrame:
    rates = estimates.loc[estimates["metric"] == "annual_growth_rate"]
    out = rates[["subject", "year", "value", "source_short"]].rename(
        columns={"value": "growth_pct", "source_short": "source"}
    )
    out["growth_pct"] = out["growth_pct"].astype(float)
    return out.sort_values("growth_pct", ascending=False).reset_index(drop=True)


def build_ai_share(estimates: pd.DataFrame) -> pd.DataFrame:
    ai = estimates.loc[estimates["metric"] == "ai_share_of_data_centre_electricity"]
    return pd.DataFrame([{
        "jurisdiction": ai["jurisdiction"].iloc[0],
        "year": int(ai["year"].iloc[0]),
        "low_pct": float(ai.loc[ai["case"] == "low estimate", "value"].iloc[0]),
        "high_pct": float(ai.loc[ai["case"] == "high estimate", "value"].iloc[0]),
        "source": ai["source_short"].iloc[0],
    }])


def build_all() -> dict[str, pd.DataFrame]:
    src = load_sources()
    validate_sources(src)
    ireland = build_ireland_annual(src["annual"])
    return {
        "ireland_annual.csv": ireland,
        "jurisdiction_share.csv": build_jurisdiction_share(ireland, src["estimates"]),
        "growth_share.csv": build_growth_share(ireland, src["estimates"]),
        "projections.csv": build_projections(src["estimates"]),
        "growth_2025.csv": build_growth_2025(src["estimates"]),
        "ai_share.csv": build_ai_share(src["estimates"]),
    }


def write(outputs: dict[str, pd.DataFrame], folder: Path) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    for name, frame in outputs.items():
        frame.to_csv(folder / name, index=False)


def check() -> int:
    outputs = build_all()
    with tempfile.TemporaryDirectory() as tmp:
        write(outputs, Path(tmp))
        mismatched = [
            name
            for name in outputs
            if not (PROCESSED / name).exists()
            or (Path(tmp) / name).read_bytes() != (PROCESSED / name).read_bytes()
        ]
    if mismatched:
        print(f"Processed files differ from a fresh rebuild: {mismatched}")
        return 1
    print(f"All {len(outputs)} processed files regenerate byte-for-byte from data/source")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Compare a fresh rebuild with data/processed")
    args = parser.parse_args()
    if args.check:
        sys.exit(check())
    outputs = build_all()
    write(outputs, PROCESSED)
    for name, frame in outputs.items():
        print(f"Wrote data/processed/{name} ({len(frame)} rows)")


if __name__ == "__main__":
    main()
