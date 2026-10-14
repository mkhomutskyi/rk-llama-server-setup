"""Keep publication scope and model identity explicit."""
from pathlib import Path
import re
import os
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PublicationTests(unittest.TestCase):
    def test_edge_helper_is_isolated_and_syntax_valid(self):
        helper = ROOT / 'scripts/download-edge-examples'
        text = helper.read_text(encoding='utf-8')
        self.assertNotRegex(text, r'\b(sudo|systemctl|apt-get)\b')
        self.assertIn('sha256sum -c -', text)
        self.assertIn('52e7645ba7c309695bec7ac98f4f005b139cf465', text)
        self.assertIn('7efa763d1da04c4c4447fa5632dc2d9c94fb3063', text)
        result = subprocess.run([os.environ.get('BASH_BIN') or 'bash', '-n', str(helper)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_all_documentation_links_and_shell_blocks(self):
        bash = os.environ.get('BASH_BIN') or shutil.which('bash')
        self.assertTrue(bash, 'Bash is required for shell syntax validation')
        for path in ROOT.rglob('*.md'):
            if '.git' in path.parts:
                continue
            text = path.read_text(encoding='utf-8')
            for target in re.findall(r'\]\(([^)]+)\)', text):
                if target.startswith(('https:', 'http:', '#')):
                    continue
                self.assertTrue((path.parent / target.split('#')[0]).exists(), target)
            for script in re.findall(r'```bash\n(.*?)\n```', text, re.S):
                result = subprocess.run([bash, '-n'], input=script, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, str(path) + ': ' + result.stderr)

    def test_no_private_host_or_credentials_in_public_text(self):
        for path in ROOT.rglob('*'):
            if '.git' in path.parts or not path.is_file():
                continue
            if path.suffix not in {'.md', '.service', '.yml', '.csv'}:
                continue
            text = path.read_text(encoding='utf-8')
            self.assertNotRegex(text, r'192\.168\.\d+\.\d+', str(path))
            self.assertNotRegex(text, r'-----BEGIN .*PRIVATE KEY-----', str(path))

    def test_tested_model_revisions_are_pinned(self):
        text = (ROOT / 'docs/model-provenance.md').read_text(encoding='utf-8')
        for revision in (
            '739965d73654c0ead8020786aa998fc813070087',
            '0720adb23527c2cd5ea01d1db067cd960327fdac',
            '530227a7d994db8eca5ab5ced2fb692b614357fd',
        ):
            self.assertIn(revision, text)
        self.assertEqual(len(set(re.findall(r'\b[a-f0-9]{64}\b', text))), 3)
