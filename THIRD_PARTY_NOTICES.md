# Attribution And License Scope

Checked 2026-10-14. This repository supplies original setup documentation,
service/Compose configuration and small helper scripts. Its [MIT license](LICENSE)
applies to those materials only, not separately obtained software or weights.
This is a practical license review, not legal certification of every deployment.

## llama.cpp And rk-llama.cpp

Credit to the ggml/llama.cpp authors and invisiofficial Rockchip backend
contributors. The pinned fork's root license is MIT, with copyright
2023-2026 The ggml authors. Retain upstream copyright/license notices when
redistributing source or binaries; dependencies may have separate notices.

- https://github.com/ggml-org/llama.cpp
- https://github.com/invisiofficial/rk-llama.cpp
- https://github.com/invisiofficial/rk-llama.cpp/blob/81eff6a45c6abbb99e26907ef7fe8f7bf3ed2c62/LICENSE

No backend source or built binaries are bundled here.

## Rockchip RKNN Runtime

Credit to Rockchip Electronics and RKNN ecosystem contributors. The build uses
the runtime supplied with the upstream fork. This repository does not bundle
or relicense that runtime, its headers, firmware or kernel image. The fork's
MIT root license alone does not establish redistribution rights for every SDK
binary. For preinstalled appliances or redistributed images, check the exact
runtime's applicable Rockchip license and retain its notices.

https://github.com/airockchip/rknn-toolkit2

Version-specific reference:
https://github.com/airockchip/rknn-toolkit2/blob/v2.3.2/LICENSE.
It is not an MIT license or an unconditional redistribution grant. This
documentation publication does not distribute the library and does not certify
the separate licensing of a preinstalled appliance or a custom OS image.

## Open WebUI

Open WebUI is a separate project, copyright Open WebUI Inc. and contributors.
Pinned v0.11.4 uses the Open WebUI License, not this repo's MIT license. It
requires redistribution notices and includes branding/non-endorsement conditions.
This guide retains default branding. Do not white-label it or imply an official
partnership. Consult the exact terms before redistributing an appliance/image.

- https://github.com/open-webui/open-webui/blob/v0.11.4/LICENSE
- https://docs.openwebui.com/license/

Compose references the official image; the image is not stored here.

## Models

No weights, tokenizers or projectors are distributed here. Both tested Gemma
files match exact Unsloth historical revisions by live SHA256 and byte size.
Those publisher model cards label Apache-2.0 and credit Google's base models.
The official Qwen file also has a pinned publisher checksum. See
[model provenance](docs/model-provenance.md). Retain applicable LICENSE/NOTICE
and conversion/modification attribution when sharing downloaded weights.

https://huggingface.co/google/gemma-4-E2B-it

This evidence applies to the named revisions, not every Gemma generation.

## Other Projects And Names

Optional edge examples download TinyLlama (independent model, Apache-2.0),
sherpa-onnx (Apache-2.0 engine; dependencies have their own notices), and
separate speech models. **SenseVoice uses the custom FunASR MODEL_LICENSE,
not sherpa-onnx's Apache license.** Retain model/source/author attribution and
review its conditions. The cited Zipformer base publisher lists Apache-2.0.
RKNN 2.2.0 is isolated per speech process, not a system runtime replacement.
No speech weights, test audio or runtime binaries are distributed here.
Pinned sources and download hashes: [edge guide](docs/edge-ai-projects.md) and
[download helper](scripts/download-edge-examples).

- https://github.com/k2-fsa/sherpa-onnx/blob/v1.13.8/LICENSE
- https://github.com/modelscope/FunASR/blob/main/MODEL_LICENSE
- https://huggingface.co/FunAudioLLM/SenseVoiceSmall
- https://huggingface.co/csukuangfj/k2fsa-zipformer-bilingual-zh-en-t

The optional GPU recipe references a separately downloaded proprietary Mali
driver package from ginkage/libmali-rockchip. It is not bundled or covered by
this MIT license. Review its upstream END_USER_LICENCE_AGREEMENT.txt and applicable
redistribution terms; package extraction is not a license grant.
Its benchmarking clause places conditions on presentation of performance
results. Keep comparisons scoped and factual, and review those terms before
public article publication. This notice is not legal advice.

The official Qwen GGUF publisher lists Apache-2.0. Keep its applicable LICENSE
and NOTICE when redistributing weights. This repo links the model but does not
redistribute it. Benchmark charts and the architecture diagram are original
figures generated from the measured aggregate data, not copied vendor art.

Armbian, Ubuntu, Docker, Orange Pi and other referenced projects retain their
licenses and trademarks. Names identify compatibility, not endorsement. Use
your own photos/screenshots with personal data removed. Check permission before
copying vendor logos/artwork into an article. No such assets are bundled here.
