# Model Check

From the repository directory on the Orange Pi:

```bash
bash scripts/verify-live-model MODEL_ID
```

Use an exact ID from `http://127.0.0.1:11436/v1/models`. The helper sends one
short request to the existing service with reasoning disabled. It does not
install, delete or restart anything. Requirements: Bash, curl and Python 3.

In a second session, observe actual NPU activity during the request:

```bash
sudo watch -n 0.5 cat /sys/kernel/debug/rknpu/load
```

An API reply alone does not prove NPU usage. See the
[setup guide](../docs/armbian-npu-open-webui.md) for build and service configuration.

## Regenerate The Figures

Optional documentation tooling, not required on the server:

```bash
python3 -m pip install matplotlib
python3 scripts/render-figures.py
```

Reads `assets/metrics.csv` and recreates the architecture and benchmark PNGs.

## Optional Edge Examples

`bash scripts/download-edge-examples "$HOME/edge-ai"` downloads and checks
the pinned TinyLlama and speech example assets without installing services or
replacing system libraries. See [the edge guide](../docs/edge-ai-projects.md)
for licenses, commands and measured limits.
