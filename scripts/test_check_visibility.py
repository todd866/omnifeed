import contextlib
import io
import subprocess
import unittest
from unittest.mock import patch
import check_visibility


class VisibilityTests(unittest.TestCase):
    def check(self, result):
        with patch('sys.argv', ['check_visibility', 'owner/repo', 'PRIVATE']), \
             patch('subprocess.run', return_value=result), \
             contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            return check_visibility.main()

    def test_private_success(self):
        self.assertEqual(self.check(subprocess.CompletedProcess([], 0, 'PRIVATE\n', '')), 0)

    def test_public_or_query_error_fail_closed(self):
        self.assertEqual(self.check(subprocess.CompletedProcess([], 0, 'PUBLIC\n', '')), 1)
        self.assertEqual(self.check(subprocess.CompletedProcess([], 1, '', 'auth failed')), 1)
        self.assertEqual(self.check(subprocess.CompletedProcess([], 0, '', '')), 1)

    def test_timeout_cannot_report_success(self):
        with patch('sys.argv', ['check_visibility', 'owner/repo', 'PRIVATE']), \
             patch('subprocess.run', side_effect=subprocess.TimeoutExpired('gh', 30)):
            with self.assertRaises(subprocess.TimeoutExpired):
                check_visibility.main()


if __name__ == '__main__':
    unittest.main()
