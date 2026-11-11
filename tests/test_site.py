"""Regression checks for source-document rendering."""
import unittest
from scripts.prepare_site import markdown_blocks


class MarkdownTests(unittest.TestCase):
    def test_adjacent_heading_and_list(self):
        rendered = markdown_blocks('## Summary\n- **Scored:** 25\n- `row-id`\n\nParagraph\ncontinued.')
        self.assertEqual(rendered, '<h2>Summary</h2><ul><li><strong>Scored:</strong> 25</li><li><code>row-id</code></li></ul><p>Paragraph continued.</p>')

    def test_source_text_is_escaped(self):
        self.assertEqual(markdown_blocks('# <script>\n\nA & B'), '<h1>&lt;script&gt;</h1><p>A &amp; B</p>')
