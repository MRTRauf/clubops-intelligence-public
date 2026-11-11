"""Regression checks for source-document rendering."""
import unittest
from scripts.prepare_site import markdown_blocks


class MarkdownTests(unittest.TestCase):
    def test_adjacent_heading_and_list(self):
        rendered = markdown_blocks('## Summary\n- **Scored:** 25\n- `row-id`\n\nParagraph\ncontinued.')
        self.assertEqual(rendered, '<h2>Summary</h2><ul><li><strong>Scored:</strong> 25</li><li><code>row-id</code></li></ul><p>Paragraph continued.</p>')

    def test_source_text_is_escaped(self):
        self.assertEqual(markdown_blocks('# <script>\n\nA & B'), '<h1>&lt;script&gt;</h1><p>A &amp; B</p>')


class ReleasePageTests(unittest.TestCase):
    def test_briefing_retains_all_source_evidence(self):
        from scripts.prepare_site import briefing_page, ROOT
        import re
        source = (ROOT / 'artifacts/briefing.md').read_text()
        output = briefing_page(source)
        for reference in re.findall(r'`([^`]+)`', source):
            self.assertIn(reference, output)
        self.assertIn('<strong>25</strong>', output)
        self.assertIn('<strong>4</strong>', output)
        self.assertIn('<strong>0</strong>', output)
        self.assertEqual(output.count('<tr>'), 11)  # Nine fixtures and two headers.
        self.assertIn('<details class="evidence">', output)
        self.assertNotIn('<details class="evidence" open', output)

    def test_briefing_keeps_club_scores_and_venues(self):
        from scripts.prepare_site import briefing_page, ROOT
        output = briefing_page((ROOT / 'artifacts/briefing.md').read_text())
        self.assertIn('<td>2025-02-09</td><td>Away</td><td>Sevilla FC</td><td>4-1</td><td>W</td>', output)
        self.assertIn('<td>2025-03-27</td><td>Home</td><td>CA Osasuna</td><td>27</td>', output)

    def test_case_study_exposes_real_evidence_and_delivery_links(self):
        from scripts.prepare_site import case_study_page, ROOT
        output = case_study_page((ROOT / 'docs/DEMO_AND_CASE_STUDY.md').read_text())
        for target in ['assets/Fixture_Desk.png', 'assets/Excel_Club_Pivot.png', 'briefing.html', 'downloads/ClubOps_Reporting.xlsx', 'dashboard/']:
            self.assertIn(target, output)
        self.assertIn('Desktop acceptance pending', output)
