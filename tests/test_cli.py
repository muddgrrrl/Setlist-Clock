from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


def cli(*args):
    return subprocess.run([sys.executable, "setlist_clock.py", *args], text=True, capture_output=True)


class SetlistClockTests(unittest.TestCase):
    def test_gap_and_rollover_use_shifted_start(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "session.tsv"
            source.write_text("# a rehearsal\nIntro\t45\nSong\t1:30\n", encoding="utf-8-sig")
            result = cli(source, "--start", "23:59", "--gap", "20")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("00:00:05 (+1d)", result.stdout)
        self.assertIn("00:01:35 (+1d)", result.stdout)
        self.assertIn("00:02:35", result.stdout)

    def test_bad_line_reports_input_line_number(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "session.tsv"
            source.write_text("# comment\nMissing tab\n")
            result = cli(source)
        self.assertEqual(result.returncode, 2)
        self.assertIn("line 2", result.stderr)
