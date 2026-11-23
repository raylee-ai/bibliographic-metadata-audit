import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("reference_audit.py")
HEADER = "document_id,reference_id\n"


class ReferenceAuditTests(unittest.TestCase):
    def invoke(self, source, after_csv, source_name="before.csv"):
        with tempfile.TemporaryDirectory() as folder:
            before = Path(folder, source_name)
            after = Path(folder, "after.csv")
            before.write_text(source, encoding="utf-8")
            after.write_text(after_csv, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(SCRIPT), str(before), str(after)],
                capture_output=True, text=True, check=False,
            )

    def test_equal_after_normalizing_and_deduplicating(self):
        result = self.invoke(
            "\ufeff" + HEADER + " W10 ,https://openalex.org/W7\nW10,W7\n",
            "reference_id,document_id,ignored\nW7,https://openalex.org/W10/,anything\n",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {
            "before_edges": 1, "after_edges": 1, "lost_edges": 0, "added_edges": 0,
            "lost": [], "added": [],
        })

    def test_changes_belong_to_document_and_are_sorted(self):
        result = self.invoke(
            HEADER + "b,W9\na,W8\na,W7\n",
            HEADER + "a,W9\na,W7\n",
        )
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(json.loads(result.stdout), {
            "before_edges": 3, "after_edges": 2, "lost_edges": 2, "added_edges": 1,
            "lost": [
                {"document_id": "a", "reference_id": "W8"},
                {"document_id": "b", "reference_id": "W9"},
            ],
            "added": [{"document_id": "a", "reference_id": "W9"}],
        })

    def test_openalex_json_supports_work_array_and_api_response(self):
        work = {"id": "https://openalex.org/W10", "referenced_works": [
            "https://openalex.org/W7", "W7", "W8",
        ]}
        empty = {"id": "W11", "referenced_works": []}
        for snapshot in (work, [empty, work], {"results": [work, empty]}):
            with self.subTest(snapshot=snapshot):
                result = self.invoke(json.dumps(snapshot), HEADER + "W10,W8\n", "works.json")
                self.assertEqual(result.returncode, 1, result.stderr)
                report = json.loads(result.stdout)
                self.assertEqual(report["before_edges"], 2)
                self.assertEqual(report["lost"], [{"document_id": "W10", "reference_id": "W7"}])

    def test_missing_or_invalid_openalex_data_is_an_input_error(self):
        examples = (
            "{", "null", '{"results": {}}', '[null]', '{"id":"W1"}',
            '{"id":"W1","referenced_works":null}', '{"id":"A1","referenced_works":[]}',
            '{"id":"W1","referenced_works":[123]}', '{"id":"W1","referenced_works":[""]}',
        )
        for source in examples:
            with self.subTest(source=source):
                result = self.invoke(source, HEADER, "works.json")
                self.assertEqual(result.returncode, 2)
                self.assertIn("works.json", result.stderr)
                self.assertEqual(result.stdout, "")

    def test_published_openalex_excerpt_matches_csv_fixture(self):
        folder = SCRIPT.parent / "examples"
        source = (folder / "accepted_works.json").read_text(encoding="utf-8")
        ids = {work["id"] for work in json.loads(source)}
        self.assertIn("https://openalex.org/W2128261329", ids)
        self.assertNotIn("https://openalex.org/W4229660601", ids)
        after_csv = (folder / "source.csv").read_text(encoding="utf-8")
        result = self.invoke(source, after_csv, "accepted_works.json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["before_edges"], 4)

    def test_header_only_csv_is_an_empty_snapshot(self):
        result = self.invoke(HEADER, HEADER)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["before_edges"], 0)

    def test_invalid_input_returns_error_instead_of_a_partial_report(self):
        for invalid in (
            "", "document_id,other\n", "document_id,reference_id,reference_id\n",
            HEADER + "a, \n", HEADER + " ,r\n", HEADER + "a,b,c\n", HEADER + 'a,"b\n',
        ):
            with self.subTest(invalid=invalid):
                result = self.invoke(HEADER, invalid)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertIn("after.csv", result.stderr)


if __name__ == "__main__":
    unittest.main()
