#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_NAME="${AUTOMORPH_ENV:-automorphz}"

if [[ "${CONDA_DEFAULT_ENV:-}" != "${ENV_NAME}" ]]; then
  if ! command -v conda >/dev/null 2>&1; then
    echo "conda is required to run ${SCRIPT_DIR}/main.py" >&2
    exit 1
  fi

  CONDA_BASE="$(conda info --base)"
  CONDA_SH="${CONDA_BASE}/etc/profile.d/conda.sh"
  if [[ ! -f "${CONDA_SH}" ]]; then
    echo "Unable to find conda initialization script at ${CONDA_SH}" >&2
    exit 1
  fi

  # shellcheck disable=SC1090
  source "${CONDA_SH}"
  conda activate "${ENV_NAME}"
fi

cd "${SCRIPT_DIR}"
exec python "${SCRIPT_DIR}/main.py" "$@"
