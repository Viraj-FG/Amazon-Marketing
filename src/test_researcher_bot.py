# test_researcher_bot.py - Unit tests for researcher_bot

import unittest
from researcher_bot import fetch_x_trends, fetch_pinterest_trends, fetch_instagram_trends, generate_report

class TestResearcherBot(unittest.TestCase):

    def test_fetch_x_trends(self):
        """Test fetching trends from X."""
        trends = fetch_x_trends()
        self.assertIsInstance(trends, list)
        self.assertTrue(len(trends) > 0)

    def test_fetch_pinterest_trends(self):
        """Test fetching trends from Pinterest."""
        trends = fetch_pinterest_trends()
        self.assertIsInstance(trends, list)
        self.assertTrue(len(trends) > 0)

    def test_fetch_instagram_trends(self):
        """Test fetching trends from Instagram."""
        trends = fetch_instagram_trends()
        self.assertIsInstance(trends, list)
        self.assertTrue(len(trends) > 0)

    def test_generate_report(self):
        """Test generating the daily report."""
        report = generate_report()
        self.assertIn("date", report)
        self.assertIn("x", report)
        self.assertIn("pinterest", report)
        self.assertIn("instagram", report)

if __name__ == "__main__":
    unittest.main()