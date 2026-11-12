import tempfile
import unittest
from pathlib import Path
from convert import convert, parse_players


class SnapshotTests(unittest.TestCase):
    def test_excludes_rows_with_only_name_or_league(self):
        result = parse_players(
            "Name,L,Index,Team,Title,Skin,AB\n"
            "Name only,,,,,,\n"
            "League only,J, , , , , \n"
            "Profile zero,O,0,,,,\n"
            "Team zero,,,0,,,\n"
            "Title only,,,,수상 타이틀,,\n"
            "Skin only,,,,,B1,\n"
            "Stat zero,,,,,,0\n"
        )
        self.assertEqual(
            [row["Name"] for row in result],
            ["Profile zero", "Team zero", "Title only", "Skin only", "Stat zero"],
        )
        self.assertEqual((result[0]["L"], result[0]["Index"]), ("O", "0"))

    def test_preserves_fields_strings_and_legacy_team_values(self):
        result = parse_players("Name,L,Index,Team,Title\n선수,O,42,6,사용자 메모\nOther,J,43,0,\nLegacy,,44,,\n")
        self.assertEqual([row["Team"] for row in result], ["6", "0", ""])
        self.assertEqual(result[0]["Title"], "사용자 메모")

    def test_rejects_html_empty_and_malformed_numbers(self):
        for value in ("<html>Error</html>", "Name,Index,Team\n", "Name,Index,Team\nA,1,-1\n", "Name,Index,Team\nA,1,2.3\n", "Name,Index,Team\nA,1,2147483648\n"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_players(value)

    def test_bad_input_never_replaces_the_previous_json(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as folder:
            source, target = Path(folder) / "data.csv", Path(folder) / "data.json"
            target.write_text("previous", encoding="utf-8")
            for invalid_csv in ("<html>Error</html>", "Name,L,Index,Team\nA,J,,\n"):
                with self.subTest(invalid_csv=invalid_csv):
                    source.write_text(invalid_csv, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        convert(source, target)
                    self.assertEqual(target.read_text(encoding="utf-8"), "previous")
            source.write_text("Name,Index,Team\nA,1,10\n", encoding="utf-8")
            convert(source, target)
            self.assertIn('"Team": "10"', target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

