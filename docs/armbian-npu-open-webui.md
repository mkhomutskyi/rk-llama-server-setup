# Armbian + rk-llama.cpp + Open WebUI

Reconciled 2026-10-14 from the installation accepted on Orange Pi 5 hardware
on **2026-10-09**. This is a pinned known-working recipe, not a claim of latest
upstream versions.

## 1. Prerequisites

- Orange Pi 5 / RK3588S, 16GB RAM, working wired Ethernet and NVMe boot.
- Armbian 26.8.1 / Ubuntu 26.04 vendor image; tested kernel
  `6.1.115-vendor-rk35xx`, built-in RKNPU driver 0.9.8.
- Login as `ai` with sudo and your own password. All commands below run in
  that user's shell unless prefixed with sudo. For another username, adjust
  ownership and service `User=` together.
- Authorized GGUF files with retained origin/license and enough free space.

Start after OS installation: no erase, repartition or image-writing commands
are supplied. For a separate reinstall, consult the
[Armbian internal-storage guide](https://docs.armbian.com/getting-started/install-to-internal-storage/)
after backups and exact disk checks. The accepted board booted NVMe-only with
microSD removed and the existing SPI loader retained, not reflashed.
Do not apply setup steps blindly over an existing deployment.

Record your system first:

If `ai` does not yet exist, create it from your current administrator session
with `sudo adduser ai` and `sudo usermod -aG sudo ai`, choosing your own
password, then sign in as ai. Do not copy another device's credentials.

```bash
cat /etc/os-release
uname -r
findmnt -M /
lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINTS
free -h
df -h /
networkctl status --no-pager
sudo journalctl -k -b --no-pager | grep -i rknpu
```

Do not assume `renderD129` is always the NPU: numbering differs by image.
Verify driver initialization and actual load during inference.

## 2. Build The Pinned Backend

Fresh-install commands, assuming these directories are not already populated:

```bash
sudo apt-get update
sudo apt-get install -y build-essential cmake git libcurl4-openssl-dev \
  ca-certificates curl python3 openssl
git clone https://github.com/mkhomutskyi/rk-llama-server-setup.git ~/rk-llama-server-setup
sudo install -d -m 755 -o ai -g ai /opt/rk-llama.cpp
git clone https://github.com/invisiofficial/rk-llama.cpp.git /opt/rk-llama.cpp
git -C /opt/rk-llama.cpp checkout --detach 81eff6a45c6abbb99e26907ef7fe8f7bf3ed2c62
cmake -S /opt/rk-llama.cpp -B /opt/rk-llama.cpp/build \
  -DCMAKE_BUILD_TYPE=Release -DLLAMA_RKNPU2=ON \
  -DGGML_VULKAN=OFF -DGGML_OPENCL=OFF -DLLAMA_BUILD_TESTS=OFF
cmake --build /opt/rk-llama.cpp/build --target llama-server llama-cli llama-bench -j4
/opt/rk-llama.cpp/build/bin/llama-server --version
git -C /opt/rk-llama.cpp rev-parse HEAD
```

Accepted compiler: GNU 15.2.0. A shallow checkout may show build number `1`
despite the same source commit; compare the commit, not just that counter.
Use source-bundled RKNN runtime 2.3.2, not an arbitrary SDK replacement.
Its accepted library SHA256:

```text
d31fc19c85b85f6091b2bd0f6af9d962d5264a4e410bfb536402ec92bac738e8
```

Inspect the checked-out library location:

```bash
find /opt/rk-llama.cpp/ggml/src/ggml-rknpu2 -name librknnrt.so -exec sha256sum {} \;
```

## 3. Models And Permissions

```bash
sudo install -d -m 755 -o ai -g ai /srv/ai-models /var/cache/rk-llama
getent group render >/dev/null || sudo groupadd -r render
sudo usermod -aG video,render ai
```

Log out and back in after changing groups. Copy authorized GGUF files into
`/srv/ai-models`, readable by `ai`, using SCP or a verified downloader. This repo
does not distribute weights or download credentials. Use one flat model directory,
separate from UI data and runtime cache; it is not the old Hugging Face cache.

For example, from your computer (replace the filename and BOARD-IP):

```bash
scp ./YOUR-LICENSED-MODEL.gguf ai@BOARD-IP:/srv/ai-models/
```

Read [third-party license notes](../THIRD_PARTY_NOTICES.md) before distributing
a preinstalled device/image. This repo's MIT license covers its own text and
helpers, not upstream binaries or model weights.

These files were tested. Live hashes and byte sizes now match pinned Unsloth
publisher revisions: see [exact provenance and downloads](model-provenance.md).

| Filename | Bytes | API ID |
|---|---:|---|
| gemma-4-E2B-it-Q8_0.gguf | 5048350848 | gemma-4-E2B-it-Q8_0 |
| gemma-4-E4B-it-Q4_0.gguf | 4836000928 | gemma-4-E4B-it-Q4_0 |

```text
E2B: 0a8488b149e1f700712c35d5bf0a3795f9dcc2563b4944d5ef2fb89375f9483e
E4B: d51af14007fe16deb45107de2411660be3b59c9e1c89bbde3bfec8ece65eeedc
```

```bash
sha256sum /srv/ai-models/*.gguf
```

No offline RKLLM conversion was needed. The NPU backend can transform weights
internally; not every architecture/quantization works. E4B Q4_0 passed a short
reply test, not broad accuracy/perplexity evaluation. That does not overturn the
historical guide's quality warnings or make all Q4 models recommended.

## 4. Native Boot Service

```bash
cd ~/rk-llama-server-setup
sudo install -m 644 deploy/llama-npu.service /etc/systemd/system/llama-npu.service
sudo systemctl daemon-reload
sudo systemctl enable --now llama-npu.service
systemctl status llama-npu --no-pager
curl -fsS http://127.0.0.1:11436/v1/models | python3 -m json.tool
```

The template uses four big CPU cores, four threads, a 4096-token context,
one loaded model, five-minute idle sleep and `LimitNOFILE=102400`. These are
accepted board settings, not universal optimal tuning.

**Cache fix:** `ProtectHome=true` blocks a default home cache. `HOME` and
`XDG_CACHE_HOME` point to the writable `/var/cache/rk-llama`. Omitting this
caused the fresh install's first-boot cache failure.

The API binds to localhost only; keep it there. WebUI uses host networking.

## 5. Docker And Open WebUI

Install Docker Engine and the Compose plugin using the
[official Ubuntu instructions](https://docs.docker.com/engine/install/ubuntu/)
for ARM64/Ubuntu resolute. Do not install conflicting Docker packages. Accepted
versions were Engine 29.9.0 and Compose 5.6.0, not a requirement to downgrade
another installation without review.

```bash
sudo systemctl enable --now docker
sudo docker version
sudo docker compose version
sudo install -d -m 755 /opt/open-webui /srv/open-webui
cd ~/rk-llama-server-setup
sudo install -m 644 deploy/compose.yml /opt/open-webui/compose.yml
```

Generate a fresh persistent secret, refusing to overwrite an existing `.env`:

```bash
sudo bash -se <<'SECRET'
test ! -e /opt/open-webui/.env
umask 077
printf 'WEBUI_SECRET_KEY=%s\n' "$(openssl rand -hex 32)" > /opt/open-webui/.env
SECRET
sudo docker compose --project-directory /opt/open-webui config --quiet
sudo install -m 644 deploy/open-webui-stack.service \
  /etc/systemd/system/open-webui-stack.service
sudo systemctl daemon-reload
sudo systemctl enable --now open-webui-stack.service
```

Compose pins the tested ARM64 slim image:

```text
ghcr.io/open-webui/open-webui:v0.11.4-slim@sha256:0487ad4a5a4b986062dedace806c3ef1e88fec38c10d1e64d6a5501c66671e5e
```

WebUI serves port 3000 and connects to `http://127.0.0.1:11436/v1` through
host networking. `OPENAI_API_KEY` is a dummy local identifier, not a cloud key.
Authentication is enabled; Ollama integration disabled. The slim image does
not bundle local embedding/speech models.

The template retains default Open WebUI branding; review upstream license
conditions before changing it.

**Clock fix:** first boot had an old date and Docker failed TLS validation.
The unit orders after `systemd-time-wait-sync.service` and retries failures.
Check actual synchronization; do not bypass TLS validation to hide a bad clock.

```bash
timedatectl status
hostname -I
```

The tested Ethernet configuration uses Netplan/systemd-networkd DHCP. Check the
actual interface (the tested one was `end1`), not an assumed `eth0`. Router
reservations are separate from board static addresses. Open
`http://YOUR-BOARD-IP:3000` on a trusted LAN and create the first administrator.
Linux and WebUI logins are separate. No account is seeded by these templates.
Keep the first-run page off untrusted networks.

## 6. Acceptance: API, NPU And WebUI

Check services individually: multi-service `is-active` can return success
even if just one service is active.

```bash
for unit in llama-npu docker open-webui-stack; do
  systemctl is-active --quiet "$unit" || exit 1
done
sudo docker ps --format 'table {{.Names}}\t{{.Status}}'
curl -fsS http://127.0.0.1:3000/health
curl -fsS http://127.0.0.1:11436/v1/models | python3 -m json.tool
```

Use exact IDs from your running server:

```bash
cd ~/rk-llama-server-setup
bash scripts/verify-live-model gemma-4-E2B-it-Q8_0
bash scripts/verify-live-model gemma-4-E4B-it-Q4_0
```

Observe NPU activity during those requests from a second SSH session:

```bash
sudo watch -n 0.5 cat /sys/kernel/debug/rknpu/load
```

Nonzero loads were observed for both models. A build flag or API reply alone
does not prove NPU usage. A "no usable GPU" warning appeared in the accepted
build despite actual NPU offload; verify the backend and hardware load.

E4B's initial 24-token request exhausted its allowance in reasoning, with no
visible answer. The helper sends `chat_template_kwargs.enable_thinking=false`,
64 output tokens and temperature 0. Five-token decode samples measured about
4.58 tokens/s E2B and 4.44 tokens/s E4B, not representative sustained benchmarks.

Check connectivity from inside WebUI, not only from your laptop:

```bash
sudo docker exec open-webui python -c 'import json,urllib.request; r=json.load(urllib.request.urlopen("http://127.0.0.1:11436/v1/models",timeout=30)); print([m["id"] for m in r["data"]])'
```

Test browser chat separately: API tests do not verify registration, streaming
or all UI features. Verify enabled services after a controlled reboot and
NVMe-only boot before permanently removing installation media.

## 7. Maintenance And Troubleshooting

```bash
sudo journalctl -u llama-npu -n 60 --no-pager
sudo journalctl -u open-webui-stack -n 60 --no-pager
sudo docker logs --tail 60 open-webui
sudo systemctl restart llama-npu
sudo systemctl restart open-webui-stack
df -h /
free -h
sudo poweroff
```

- Keep the pinned backend and working vendor kernel available. Upgrade one
  component at a time; repeat model, NPU and WebUI checks.
- Pulling a digest-pinned image alone does not upgrade it. Review a new ARM64
  tag/digest before editing Compose and redeploying.
- Back up `/srv/ai-models`, `/opt/open-webui` including its private `.env`,
  and `/srv/open-webui`. Stop WebUI while copying its SQLite data for a
  consistent backup; do not copy an actively written database blindly.
- Preserve files/license/hash records before model changes. Restart the
  backend and check model IDs after adding files.
- Fresh-image root console autologin overrides were removed at acceptance.
  Check new image getty overrides for `--autologin root` and require normal
  login. Remove temporary install keys only after confirming normal owner
  SSH access. Keep SSH enabled for headless administration.
- Bluetooth HCIAttach failed independently of working AI services. Record
  the limitation, rather than claiming all services healthy or blindly
  disabling hardware functionality.

No private passwords, host keys, disk serials/UUIDs or fixed LAN addresses are
needed to reproduce this software layout. Do not import them from another host.

## 8. CPU And GPU Alternatives

The default above is the accepted NPU boot service. The October 14 comparison
also tested genuine CPU-only and vendor Mali Vulkan builds. Follow the
[separate backend guide](cpu-npu-vulkan.md) for driver extraction, build flags,
alternative service templates and updating WebUI's backend dependency.
Read [measured results](benchmarks.md) before assuming acceleration is faster.
