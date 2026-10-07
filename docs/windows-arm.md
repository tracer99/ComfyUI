# Windows ARM

This is a fork of Comfy-Org/ComfyUI with its original history. ARM-specific changes are ported from Sasen12/ComfyUI-ARM-Windows at `8514053`. The upstream base is `b00c6e95279053474955540ba4f551646722b9aa` (ComfyUI 0.39.0), checked on 2026-10-07. Upstream licensing and attribution are retained.

## DirectML setup

1. Install x64 Python 3.11 or 3.12, including pip. Windows ARM runs this interpreter under emulation.
2. Clone this fork's `codex/windows-arm` branch.
3. Run `start-arm.cmd`. It creates `.venv`, installs the dependencies, and starts ComfyUI at http://127.0.0.1:8188 with custom nodes disabled.

```powershell
git clone --branch codex/windows-arm https://github.com/tracer99/ComfyUI.git
cd ComfyUI
.\start-arm.cmd
```

Set `COMFYUI_ARM_PYTHON` to an interpreter's full path if automatic discovery selects the wrong Python. Use `start-arm-full.cmd` to enable custom nodes, `start-arm.cmd -CpuOnly` for CPU execution, or `start-arm.cmd -Port 8189` to select another port. Dependencies and bootstrap stamps are local to this checkout.

DirectML currently requires PyTorch 2.4.1. The runtime requirements also pin Transformers and Hugging Face Hub to compatible versions. A version-scoped schema adapter allows current comfy-kitchen custom operations to import with that PyTorch release. Upstream requirements remain intact. Features requiring newer PyTorch kernels or CUDA are not validated with DirectML.

The port handles shared Adreno memory, opaque DirectML tensor storage, split attention, and one CPU retry after a DirectML memory failure. Retrying runs the prompt again; workflows with external side effects should use CPU explicitly if repeated execution would be undesirable.

## Experimental QNN

`start-arm-qnn.cmd` selects native ARM64 Python 3.11 and a separate `.venv-qnn`. It runs the surrounding workflow on CPU and attempts QNN denoising only for supported model configurations. The QNN diagnostic nodes expose provider and device status; CPU startup alone does not establish NPU acceleration.

Native QNN dependency installation is **not validated** on the development machine. Current upstream dependencies `blake3` and `cryptography` require Rust builds for this interpreter; both failed during linking with the installed toolchain. NPU discovery, ONNX export, and real-model inference therefore remain unverified. Use DirectML for the working local installation.

## Validation

The compatibility tests cover host/interpreter detection, attention memory recovery, opaque storage, current comfy-kitchen operations, QNN selection and fallback, logging, and prompt CPU retry. The Windows ARM workflow runs these tests and CPU startup on Windows x64 with Python 3.11 and 3.12; hosted CI does not have an Adreno GPU or Snapdragon NPU.

Local checks on the Qualcomm Adreno X1-85 include CPU startup, dependency consistency, a small UNet forward pass matching CPU output, and an API workflow saving an image. These use the current upstream frontend and core dependencies. No model checkpoint is included. Full checkpoint-based image generation and custom-node compatibility require separate testing with the models and extensions you intend to use.

## Updating upstream

Keep `origin` pointed at this fork and `upstream` at Comfy-Org/ComfyUI. Commit local changes before merging:

```powershell
git remote add upstream https://github.com/Comfy-Org/ComfyUI.git # only once
git fetch upstream
git switch codex/windows-arm
git merge upstream/master
.\bootstrap-arm.cmd
```

Resolve changes to model loading, memory management, execution, attention, and dependency requirements carefully. Run the compatibility tests and CPU startup check in `.github/workflows/windows-arm.yml`, then test a DirectML workflow on actual ARM hardware before pushing. The shared upstream history makes subsequent merges reviewable.
