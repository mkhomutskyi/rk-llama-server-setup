"""Offline checks of backend templates and benchmark data, not board acceptance."""
import csv
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class BackendDocsTests(unittest.TestCase):
    def test_switch_uses_full_unit_not_dependency_reset(self):
        text = (ROOT / 'docs/cpu-npu-vulkan.md').read_text()
        self.assertIn('deploy/open-webui-stack.service', text)
        self.assertNotIn("printf '[Unit]\\nRequires=\\n", text)

    def test_cpu_uses_distinct_binary(self):
        text = (ROOT / "deploy/llama-cpu.service").read_text()
        self.assertIn("build-cpu/bin/llama-server", text)
        self.assertIn("--device none --n-gpu-layers 0", text)
        self.assertIn("Conflicts=llama-npu.service llama-vulkan.service", text)

    def test_gpu_uses_process_specific_driver(self):
        text = (ROOT / "deploy/llama-vulkan.service").read_text()
        self.assertIn("Environment=VK_DRIVER_FILES=/opt/rk-mali-vulkan/", text)
        self.assertIn("--device Vulkan0", text)
        self.assertIn("--no-kv-offload --no-op-offload", text)
        self.assertIn("Conflicts=llama-npu.service llama-cpu.service", text)

    def test_services_remain_local_and_small_context(self):
        for name in ("llama-cpu", "llama-vulkan"):
            text = (ROOT / "deploy" / f"{name}.service").read_text()
            self.assertIn("--host 127.0.0.1 --port 11436", text)
            self.assertIn("--ctx-size 512", text)
            self.assertIn("User=ai", text)

    def test_aggregate_results(self):
        with (ROOT / "assets/metrics.csv").open(newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 6)
        for row in rows:
            self.assertEqual(row["repetitions"], "2")
        qwen = {r["backend"]: r for r in rows if r["model"] == "Qwen3-14B Q6_K"}
        self.assertEqual(float(qwen["CPU"]["generation_tps"]), 1.66)
        self.assertEqual(float(qwen["GPU"]["prompt_tps"]), .45)

    def test_images_and_scope_notes(self):
        for name in ("architecture", "generation", "prompt"):
            self.assertTrue((ROOT / "assets" / f"{name}.png").is_file())
        text = (ROOT / "docs/benchmarks.md").read_text()
        self.assertIn("14 GiB cgroup cap", text)
        self.assertIn("No simultaneous CPU+GPU+NPU", text)

if __name__ == "__main__":
    unittest.main()
