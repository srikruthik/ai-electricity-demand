"""Each validation check must reject the broken data it exists to catch.

Run from the repository root: python -m unittest discover tests
"""

import unittest

from src import pipeline


class ValidationRejectsBadData(unittest.TestCase):
    def setUp(self):
        self.src = pipeline.load_sources()

    def assertRejected(self):
        with self.assertRaises(ValueError):
            pipeline.validate_sources(self.src)

    def test_clean_sources_pass(self):
        pipeline.validate_sources(self.src)

    def test_missing_annual_year(self):
        self.src["annual"] = self.src["annual"].iloc[1:]
        self.assertRejected()

    def test_mistyped_annual_value(self):
        self.src["annual"].loc[5, "data_centres_gwh"] += 100
        self.assertRejected()

    def test_missing_quarterly_year(self):
        q = self.src["quarterly"]
        self.src["quarterly"] = q.loc[q["year"] != 2020]
        self.assertRejected()

    def test_mistyped_quarterly_value(self):
        self.src["quarterly"].loc[10, "data_centres_gwh"] += 50
        self.assertRejected()

    def test_duplicate_estimate_id(self):
        e = self.src["estimates"]
        e.loc[1, "estimate_id"] = e.loc[0, "estimate_id"]
        self.assertRejected()

    def test_percentage_out_of_range(self):
        e = self.src["estimates"]
        e.loc[e["unit"] == "percent", "value"] = 150
        self.assertRejected()


class OutputsMatchPublishedFigures(unittest.TestCase):
    def test_headline_growth_share(self):
        growth = pipeline.build_all()["growth_share.csv"]
        ireland = growth.loc[growth["jurisdiction"] == "Ireland", "share_pct"].iloc[0]
        self.assertAlmostEqual(ireland, 76.6, places=1)

    def test_latest_share_matches_cso(self):
        annual = pipeline.build_all()["ireland_annual.csv"]
        self.assertAlmostEqual(annual.iloc[-1]["data_centre_share_pct"], 23.2, places=1)


if __name__ == "__main__":
    unittest.main()
