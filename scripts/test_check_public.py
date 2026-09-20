import unittest
import contextlib
import io
import os
import pathlib
import subprocess
import tempfile
from check_public import problems, run


class PublicBoundaryTests(unittest.TestCase):
    def test_runtime_paths_are_blocked(self):
        for path in ("data/library.json", "media/song.flac", ".env.local",
                     "nested/playback-history.json", "library.sqlite3-wal", "secret.pem",
                     "library.sqlite-shm", "library.sqlite-wal", "library.db-journal",
                     "Secrets/a.txt", "Data/example.json", ".Env", "credentials.json"):
            with self.subTest(path=path):
                self.assertTrue(problems(path, b""))

    def test_code_docs_and_examples_allowed(self):
        for path in ("docs/private-data.md", ".env.example", "software/runtime/omni.py"):
            self.assertEqual(problems(path, b"documented data path"), [])

    def test_credentials_blocked_without_echo(self):
        token = b"gh" + b"p_" + b"x" * 36
        self.assertEqual(problems("settings.txt", token), ["possible credential"])

    def test_index_contents_are_checked_even_if_worktree_is_cleaned(self):
        with tempfile.TemporaryDirectory() as directory:
            previous = os.getcwd()
            try:
                os.chdir(directory)
                subprocess.run(["git", "init", "-q"], check=True)
                token = b"gh" + b"p_" + b"z" * 36
                pathlib.Path("settings.txt").write_bytes(token)
                subprocess.run(["git", "add", "settings.txt"], check=True)
                pathlib.Path("settings.txt").write_text("no token in worktree")
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    self.assertEqual(run(staged=True), 1)
                    self.assertEqual(run(), 1)
                self.assertNotIn(token.decode(), stderr.getvalue())
                pathlib.Path("settings.txt").write_text("safe")
                subprocess.run(["git", "add", "settings.txt"], check=True)
                pathlib.Path("untracked.txt").write_bytes(token)
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(run(), 0)
            finally:
                os.chdir(previous)


if __name__ == "__main__":
    unittest.main()
