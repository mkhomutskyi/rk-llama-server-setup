# Orange Pi 5 AI Box: CPU, NPU And GPU

Practical setup notes for a 16GB Orange Pi 5 running native **rk-llama.cpp**
with GGUF models and Docker **Open WebUI**. This is not the older RKLLama
Docker/.rkllm conversion stack.

## Start Here

**[Current implementation guide](docs/armbian-npu-open-webui.md)**

Initial boot/UI acceptance: **2026-10-09**. CPU/NPU/Vulkan comparison and
separate backend reboot checks: **2026-10-14**.
These are the versions actually used, not a claim of latest upstream releases.

| Component | Verified October baseline |
|---|---|
| Hardware | Orange Pi 5 / RK3588S, 16GB RAM, NVMe-only boot |
| OS | Armbian 26.8.1 / Ubuntu 26.04, vendor kernel 6.1.115 |
| NPU driver / runtime | RKNPU 0.9.8 / source-bundled RKNN 2.3.2 |
| Backend | invisiofficial/rk-llama.cpp, commit `81eff6a45c6abbb99e26907ef7fe8f7bf3ed2c62` |
| Build | Release; NPU on, Vulkan/OpenCL off; GNU 15.2.0 |
| Models tested | Gemma 4 E2B Q8_0 and E4B Q4_0 GGUF |
| Model API | Loopback only, `127.0.0.1:11436/v1` |
| Browser UI | Open WebUI 0.11.4 slim, port 3000, authentication enabled |
| Networking | Wired DHCP; no fixed board IP required |

Both model smoke tests returned the expected reply with nonzero NPU activity.
WebUI container health and its connection to the model API passed. Browser
availability was owner-confirmed; first WebUI account creation was deliberately
left to the new owner. Bluetooth initialization failed in this image and is
not a verified feature. LM Studio and vision are outside this baseline.
Vulkan was subsequently tested with an isolated vendor Mali driver, without
changing the kernel. It works, but was slower than CPU in the measured workloads.

## Choose A Backend

- **CPU:** use a separate build with NPU and Vulkan disabled. In this fork,
  `--device none` alone did not prevent NPU activity.
- **NPU:** the original boot service and GGUF recipe below; verify real load.
- **GPU:** experimental Vulkan path on the same vendor kernel, using a pinned
  Mali userspace driver and host-side KV cache. No kernel replacement required.

See [backend setup and switching](docs/cpu-npu-vulkan.md) and
[measured results](docs/benchmarks.md). These are alternative runs, not proof
of simultaneous CPU+GPU+NPU acceleration.

**[Practical edge projects](docs/edge-ai-projects.md):** tested TinyLlama,
SenseVoice and small Zipformer NPU transcription, with verified downloads and
clear limits. A smaller model does not automatically run faster on the NPU.

![Measured token generation](assets/generation.png)

## Files

- [Current guide](docs/armbian-npu-open-webui.md): build, model placement,
  Docker/UI setup, boot services, validation and maintenance.
- [Deployment templates](deploy/): matching service/Compose settings, no secrets.
- [Model verification helper](scripts/verify-live-model): test an existing
  model through the running API; observe NPU load separately.
- [Script usage](scripts/README.md) and [offline tests](tests/test_verify_live_model.py).
- [CPU/NPU/GPU guide](docs/cpu-npu-vulkan.md): separate builds, vendor GPU
  driver, model download, service templates and selecting a WebUI backend.
- [Benchmark method and results](docs/benchmarks.md): short tests and limits.

The October layout uses `/opt/rk-llama.cpp`, `/srv/ai-models`,
`/var/cache/rk-llama`, `/opt/open-webui` and `/srv/open-webui`.

## Safety And Scope

No model weights, image backups, private keys, passwords or WebUI data are
distributed here. Obtain authorized GGUF files and retain their license/origin.
The tested files match pinned publisher revisions: see
[model provenance](docs/model-provenance.md) for hashes, attribution and downloads.
Choose your own Linux password and WebUI administrator account; keep LAN-only.
This guide starts after a suitable OS is installed: no disk erase or imaging.

## License And Attribution

Original guide text, templates and helper scripts are [MIT licensed](LICENSE).
Upstream software/model terms remain separate: see
[attribution and notices](THIRD_PARTY_NOTICES.md). Public examples retain default
Open WebUI branding. No weights, SDK binaries or vendor artwork are bundled.

This is an independent guide, not a vendor-endorsed product.
