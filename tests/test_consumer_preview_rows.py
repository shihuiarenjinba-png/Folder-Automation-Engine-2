"""Test the presentation layer with no filesystem mutations."""
import json
import unittest
from consumer_preview_ui import parse_preview_rows

class PreviewTableTests(unittest.TestCase):
    def event(self, *, action="copy", dry_run=True):
        return json.dumps({"file":"C:/demo/inbox/report.pdf","action":action,
                           "destination":"C:/demo/processed/report.pdf","dry_run":dry_run})

    def test_planned_copy(self):
        self.assertEqual(parse_preview_rows(self.event(),japanese=True),
                         [("report.pdf","processed/report.pdf","コピー","予定")])
    def test_blocked_copy_is_not_approved(self):
        s=self.event()+"\nBLOCKED destination exists: C:/demo/processed/report.pdf"
        self.assertEqual(parse_preview_rows(s,japanese=True)[0][-1],"上書き回避")
    def test_ordinary_logs_are_not_file_actions(self):
        self.assertEqual(parse_preview_rows("SKIP unfinished download: x.part\n0 file(s)",japanese=True),[])
    def test_row_limit(self):
        self.assertEqual(len(parse_preview_rows("\n".join([self.event()]*8),japanese=False,max_rows=3)),3)
    def test_move_not_dry_run(self):
        self.assertEqual(parse_preview_rows(self.event(action="move",dry_run=False),japanese=False)[0][-2:],("Move","Execution log"))

if __name__ == "__main__":
    unittest.main()
