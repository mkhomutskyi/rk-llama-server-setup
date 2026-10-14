# Exact Model Provenance

Verified 2026-10-14 by comparing live SHA256 and byte size with Hugging Face
publisher metadata at the pinned revisions below. No weights are bundled.

| File | Publisher | Revision | Bytes |
|---|---|---|---:|
| gemma-4-E2B-it-Q8_0.gguf | unsloth/gemma-4-E2B-it-GGUF | 739965d73654c0ead8020786aa998fc813070087 | 5048350848 |
| gemma-4-E4B-it-Q4_0.gguf | unsloth/gemma-4-E4B-it-GGUF | 0720adb23527c2cd5ea01d1db067cd960327fdac | 4836000928 |
| Qwen3-14B-Q6_K.gguf | Qwen/Qwen3-14B-GGUF | 530227a7d994db8eca5ab5ced2fb692b614357fd | 12121937248 |

SHA256, in the same order:

```text
0a8488b149e1f700712c35d5bf0a3795f9dcc2563b4944d5ef2fb89375f9483e
d51af14007fe16deb45107de2411660be3b59c9e1c89bbde3bfec8ece65eeedc
ec1f1d1421d7636a23e17645cac6fda39ee4b5f1f11e42eb09238089705ef699
```

Publisher model cards label these revisions Apache-2.0. Google's Gemma base
model is credited by Unsloth; Qwen publishes its own GGUF. Retain applicable
LICENSE/NOTICE and conversion attribution if redistributing downloaded files.
Matching a digest establishes file identity, not independent model-quality
validation or a guarantee that every upstream artifact has been audited.

## Publisher Links

- [Gemma E2B tested revision](https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF/tree/739965d73654c0ead8020786aa998fc813070087)
- [Gemma E4B tested revision](https://huggingface.co/unsloth/gemma-4-E4B-it-GGUF/tree/0720adb23527c2cd5ea01d1db067cd960327fdac)
- [Qwen tested revision](https://huggingface.co/Qwen/Qwen3-14B-GGUF/tree/530227a7d994db8eca5ab5ced2fb692b614357fd)

Newer Gemma files have different chat-template metadata and checksums. Do not
replace these files with current main and attribute the old benchmarks to them.

## Download The Tested Small Model

Run as the configured ai user, which owns the model directory. Refuse to
overwrite an existing file. Check free space first (about 5.05 GB download).

```bash
cd /srv/ai-models
test ! -e gemma-4-E2B-it-Q8_0.gguf
test ! -e gemma-4-E2B-it-Q8_0.gguf.part
curl -fL --retry 3 -o gemma-4-E2B-it-Q8_0.gguf.part \
  https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF/resolve/739965d73654c0ead8020786aa998fc813070087/gemma-4-E2B-it-Q8_0.gguf
printf '%s  gemma-4-E2B-it-Q8_0.gguf.part\n' \
  0a8488b149e1f700712c35d5bf0a3795f9dcc2563b4944d5ef2fb89375f9483e | sha256sum -c -
mv -n gemma-4-E2B-it-Q8_0.gguf.part gemma-4-E2B-it-Q8_0.gguf
```
