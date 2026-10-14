"""Offline contract tests; no board, Docker daemon or network calls."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASH = os.environ.get('BASH_BIN') or shutil.which('bash')


@unittest.skipUnless(BASH, 'Bash is required')
class VerificationTests(unittest.TestCase):
    def run_helper(self, args, mode='ok'):
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            (temp / 'python3').write_text(
                '#!/usr/bin/env bash\nexec "$TEST_PYTHON" "$@"\n', encoding='utf-8', newline='\n')
            (temp / 'curl').write_text('''#!/usr/bin/env bash
set -euo pipefail
while (($#)); do
  if [[ "$1" == --data-binary ]]; then
    printf '%s' "$2" > "$TEST_PAYLOAD"
    break
  fi
  shift
done
case "$TEST_MODE" in
  ok) printf '%s' '{"model":"mock","choices":[{"message":{"content":"NPU reinstall passed"}}]}' ;;
  wrong) printf '%s' '{"choices":[{"message":{"content":"other reply"}}]}' ;;
  broken) printf '%s' 'not json' ;;
  http) exit 22 ;;
esac
''', encoding='utf-8', newline='\n')
            for name in ['python3', 'curl']:
                (temp / name).chmod(0o755)
            env = dict(os.environ, TEST_PYTHON=sys.executable.replace('\\', '/'),
                       TEST_PAYLOAD=str(temp / 'payload.json').replace('\\', '/'),
                       TEST_MODE=mode)
            mock_path = str(temp).replace('\\', '/')
            if os.name == 'nt':
                mock_path = '/' + mock_path[0].lower() + mock_path[2:]
            # Set PATH inside Bash: Windows PATH separators differ from POSIX.
            result = subprocess.run(
                [BASH, '-c', 'export PATH="$1:$PATH"; shift; bash "$@"', 'test',
                 mock_path,
                 str(ROOT / 'scripts' / 'verify-live-model').replace('\\', '/'), *args],
                env=env, capture_output=True, text=True)
            payload = temp / 'payload.json'
            return result, json.loads(payload.read_text()) if payload.exists() else None

    def test_valid_reply_and_safe_model_encoding(self):
        model = 'model "quoted"; $(touch should-not-exist)'
        result, payload = self.run_helper([model])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(payload['model'], model)
        self.assertFalse(payload['chat_template_kwargs']['enable_thinking'])
        self.assertEqual(payload['max_tokens'], 64)
        self.assertIn('confirm actual NPU activity separately', result.stdout)

    def test_missing_argument(self):
        result, payload = self.run_helper([])
        self.assertEqual(result.returncode, 2)
        self.assertIsNone(payload)

    def test_bad_reply(self):
        result, _ = self.run_helper(['example'], 'wrong')
        self.assertNotEqual(result.returncode, 0)

    def test_bad_json(self):
        result, _ = self.run_helper(['example'], 'broken')
        self.assertNotEqual(result.returncode, 0)

    def test_http_failure(self):
        result, _ = self.run_helper(['example'], 'http')
        self.assertNotEqual(result.returncode, 0)

    def test_shell_and_documentation_syntax(self):
        scripts = [(ROOT / 'scripts' / 'verify-live-model').read_text()]
        guide = (ROOT / 'docs' / 'armbian-npu-open-webui.md').read_text()
        scripts.extend(re.findall(r'```bash\n(.*?)\n```', guide, re.S))
        for script in scripts:
            result = subprocess.run([BASH, '-n'], input=script,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_current_local_links(self):
        for path in [ROOT / 'README.md', ROOT / 'docs' / 'armbian-npu-open-webui.md',
                     ROOT / 'scripts' / 'README.md', ROOT / 'THIRD_PARTY_NOTICES.md']:
            for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
                if target.startswith(('https:', 'http:', '#')):
                    continue
                self.assertTrue((path.parent / target.split('#')[0]).exists(), target)


if __name__ == '__main__':
    unittest.main()
