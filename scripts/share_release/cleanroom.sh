#!/usr/bin/env bash
# The clean room (plan step 7): a fresh container with an empty home folder, no Git and no login of this machine,
# holding only the release zip; it unpacks the zip, keeping each file's mode, and runs the release's own check
# script as a recipient would (./scripts/check.sh, so the executable bit is proven too).
#
#   scripts/share_release/cleanroom.sh <release.zip> [<log file>]
#
# The image is uv's Python 3.12 image (ghcr.io/astral-sh/uv), so the checks' dependencies can be fetched from
# PyPI; nothing else of this machine is mounted or passed. Docker is not inside the room, so the store rows run
# outside it (validate.py, on test stores); this proves the setup, the builders, the regression and every test.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
zip="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
log="${2:-cleanroom.log}"
extract="$(python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import publish; print(publish.EXTRACT_CODE)' "$HERE")"
docker run --rm -v "$zip":/release.zip:ro -e HOME=/tmp/home -e GIT_CONFIG_NOSYSTEM=1 -e CHECK_WORKERS=4 -e EXTRACT="$extract" \
  -w /tmp ghcr.io/astral-sh/uv:python3.12-bookworm bash -c '
    set -e; mkdir -p /tmp/home /tmp/room; cd /tmp/room
    python3 -c "$EXTRACT" /release.zip .
    cd "$(ls -d */ | head -1)"
    echo "room: $(pwd); python $(python3 --version); uv $(uv --version); git: $(command -v git || echo none)"
    ./scripts/check.sh
  ' 2>&1 | tee "$log"
