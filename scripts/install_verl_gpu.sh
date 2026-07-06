#!/usr/bin/env bash
set -euo pipefail

# Conservative install helper for a fresh CUDA rental box. If you use a managed
# veRL Docker image, skip this and install this repo inside that image instead.
python3 -m pip install --upgrade pip
python3 -m pip install -e '.[data,gpu]'
python3 -m pip install 'verl[vllm]'

echo "Installed local package and veRL. Verify CUDA with:"
echo "python3 - <<'PY'"
echo "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no cuda')"
echo "PY"
