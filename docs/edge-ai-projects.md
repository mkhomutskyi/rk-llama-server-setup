# Practical Edge AI Examples

Checked and tested 2026-10-14 on the [baseline board](armbian-npu-open-webui.md).
These are optional experiments, not new boot services or a complete voice assistant.

## What The NPU Is For

An NPU accelerates supported neural-network operations. It is useful for local
speech, vision and some language-model workloads, but needs compatible models,
runtime, operators and input shapes. The advertised TOPS number is not a promise
of LLM tokens per second. RK3588 uses shared system memory; model-file size is
not peak runtime memory. CPU preprocessing, decoding and unsupported operations
still matter. No power-efficiency measurements were made here.

The GGUF LLM route uses rk-llama.cpp. The speech route below uses sherpa-onnx
and separate `.rknn` models. They are not interchangeable formats.

## Measured Small-Model Results

TinyLlama is an independent 1.1B model using Llama architecture, not a new Meta
release. The tested Q8_0 file is 1,170,781,568 bytes (1.09 GiB).

| TinyLlama Q8_0 | Prompt tokens/sec | Generated tokens/sec |
|---|---:|---:|
| CPU-only | 113.20 +/- 0.13 | 21.93 +/- 0.01 |
| NPU + CPU | 154.63 +/- 0.22 | 11.88 +/- 0.22 |

Same pinned fork, pp64/tg32, batch/microbatch 128, four big-core threads,
two repetitions, host KV cache, operation offload disabled. CPU had no sampled
NPU activity; the NPU benchmark peaked at 81%. Loading/conversion is excluded.
TinyLlama returned text, but its suggested "offline" projects included online
services. Use it for learning, not trusted planning or autonomous commands.

## Speech That Actually Ran

| Example | Audio duration | Reported decode time | RTF |
|---|---:|---:|---:|
| SenseVoice CPU int8 | 7.152 sec | 0.341 sec median, 3 runs | 0.048 |
| SenseVoice NPU, 20-second export | same clip | 0.909 sec median, 3 runs | 0.127 |
| Small bilingual Zipformer NPU | 10 sec | 1.1 sec, 1 run | 0.11 |

RTF means decode time divided by audio duration; below 1 is faster than real
time. These times exclude recognizer initialization. Total CLI wall time was
roughly 2-4 seconds, including initialization. SenseVoice exports differ in
precision and fixed-shape padding: this is not an identical-precision CPU/NPU
ranking. CPU was faster for this particular clip. No word-error-rate evaluation
was performed, and the transcriptions differed.

NPU load was observed during speech decoding (SenseVoice peak 53%, Zipformer
29%). Counters can retain the preceding sample: do not attribute activity at
CPU process startup to CPU-model offload. Ordinary-user NPU transcription also
passed. No microphone, live streaming latency, wake word or TTS pipeline was tested.

Zipformer's three RKNN files total 60,514,379 bytes (57.7 MiB); SenseVoice's
RKNN file is 485,978,518 bytes. Compact speech models are a practical NPU example
without multi-gigabyte LLM weights.

## Download Verified Examples

Read [license notices](../THIRD_PARTY_NOTICES.md) before downloading. The helper
fetches publisher assets and checks SHA256; it does not bundle weights, replace
system libraries or touch boot services. Keep the downloaded LICENSE/README files.
Allow several GB of free space. Run as your normal user:

```bash
bash scripts/download-edge-examples "$HOME/edge-ai"
```

TinyLlama converter: TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF, revision
`52e7645ba7c309695bec7ac98f4f005b139cf465`, Apache-2.0. Its source model is
[TinyLlama/TinyLlama-1.1B-Chat-v1.0](https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0).
All tested download hashes are pinned in the helper.

Speech engine: sherpa-onnx v1.13.8, commit
`11afbd009a7f8c08f4bcf2fc1b265d0df4670fbf`. The speech examples use a process-local
RKNN 2.2.0 library from Rockchip commit
`7efa763d1da04c4c4447fa5632dc2d9c94fb3063`. Upstream warns that other runtime
versions can fail for these models. **Do not downgrade the LLM's RKNN 2.3.2.**

## Try NPU Transcription

Use a mono 16 kHz WAV, or first use the publisher's included sample:

```bash
base="$HOME/edge-ai"
bin="$base/sherpa-onnx-v1.13.8-rknn-linux-aarch64-shared/bin"
model="$base/sherpa-onnx-rk3588-20-seconds-sense-voice-zh-en-ja-ko-yue-2024-07-17"
LD_LIBRARY_PATH="$base/lib:$base/sherpa-onnx-v1.13.8-rknn-linux-aarch64-shared/lib" \
  "$bin/sherpa-onnx-offline" --provider=rknn --num-threads=-4 \
  --sense-voice-model="$model/model.rknn" --tokens="$model/tokens.txt" \
  "$model/test_wavs/en.wav"
```

Here `-4` selects all three NPU cores; it is not a negative CPU thread count.
This export pads short clips to 20 seconds and truncates longer clips. Use VAD
and supported chunking for longer recordings; do not silently discard audio.

Small bilingual Zipformer (Chinese/English):

```bash
base="$HOME/edge-ai"
bin="$base/sherpa-onnx-v1.13.8-rknn-linux-aarch64-shared/bin"
model="$base/sherpa-onnx-rk3588-streaming-zipformer-small-bilingual-zh-en-2023-02-16"
LD_LIBRARY_PATH="$base/lib:$base/sherpa-onnx-v1.13.8-rknn-linux-aarch64-shared/lib" \
  "$bin/sherpa-onnx" --provider=rknn --num-threads=-4 \
  --encoder="$model/encoder.rknn" --decoder="$model/decoder.rknn" \
  --joiner="$model/joiner.rknn" --tokens="$model/tokens.txt" \
  "$model/test_wavs/0.wav"
```

Use [backend instructions](cpu-npu-vulkan.md) for TinyLlama CPU/NPU trials.
Pass the helper's GGUF path instead of a Gemma path. Stop competing inference
jobs for repeatable measurements, then restore your selected backend.

## Projects To Build Next

- **Tested:** browser-based local chat; short recorded-file transcription.
- **Proposed:** push-to-talk recording -> ASR -> local LLM -> CPU TTS.
- **Proposed:** a limited voice-command router with explicit confirmation for
  home automation. Never execute arbitrary model-generated shell commands.
- **Vendor-supported, not tested here:** camera classification/object detection
  using [Rockchip model-zoo examples](https://github.com/airockchip/rknn_model_zoo).
- **Not tested:** Whisper conversion, keyword spotting, USB microphone and
  simultaneous LLM/ASR contention. Do not infer these from a file-transcription pass.

## Sources

- [Sherpa RKNN install](https://k2-fsa.github.io/sherpa/onnx/rknn/install.html)
- [Sherpa models and runtime constraints](https://k2-fsa.github.io/sherpa/onnx/rknn/models.html)
- [SenseVoice model](https://huggingface.co/FunAudioLLM/SenseVoiceSmall)
- [FunASR model license](https://github.com/modelscope/FunASR/blob/main/MODEL_LICENSE)
- [Zipformer base model](https://huggingface.co/csukuangfj/k2fsa-zipformer-bilingual-zh-en-t/tree/e2382758de9a0219b4efe682b95af30b399db3b8)
