#!/usr/bin/env bash
set -euo pipefail

# Conservative install helper for a fresh CUDA rental box. If you use a managed
# veRL Docker image, skip this and install this repo inside that image instead.
VENV="${VENV:-.venv-gpu}"
if [ ! -x "${VENV}/bin/python" ]; then
  python3 -m venv "${VENV}"
fi
"${VENV}/bin/python" -m pip install --upgrade pip
"${VENV}/bin/python" -m pip install -e '.[data,gpu]'
"${VENV}/bin/python" -m pip install 'verl[vllm]'

echo "Installed local package and veRL. Verify CUDA with:"
echo "${VENV}/bin/python - <<'PY'"
echo "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no cuda')"
echo "PY"
