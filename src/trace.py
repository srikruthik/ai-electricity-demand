"""Trace the headline share of growth from the processed file the app reads.

Run from the repository root: python -m src.trace
"""

import pandas as pd

from src.pipeline import PROCESSED

annual = pd.read_csv(PROCESSED / "ireland_annual.csv")
first, last = annual.iloc[0], annual.iloc[-1]
dc = int(last["data_centres_gwh"] - first["data_centres_gwh"])
other = int(last["other_gwh"] - first["other_gwh"])

print("From data/processed/ireland_annual.csv (built from data/source/cso_mec02_annual.csv)\n")
print(annual.loc[[0, len(annual) - 1], ["year", "data_centres_gwh", "other_gwh"]].to_string(index=False))
print(f"\nIncrease in data centres:        {dc:,} GWh")
print(f"Increase in all other customers: {other:,} GWh")
print(f"Data centres' share of growth:   {dc:,} / ({dc:,} + {other:,}) = {dc / (dc + other) * 100:.1f}%")
