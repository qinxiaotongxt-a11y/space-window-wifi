#!/bin/bash
set -e
cd "$(dirname "$0")/relay"
if command -v python3.12 >/dev/null 2>&1; then
  relay_python=python3.12
else
  relay_python=python3
fi
if ! "$relay_python" -c 'import sys; assert sys.version_info >= (3, 10)' >/dev/null 2>&1; then
  echo '请先安装 Python 3.12：https://www.python.org/downloads/'
  read -r -p '按回车退出。' ignored
  exit 1
fi
if ! command -v deno >/dev/null 2>&1; then
  echo '请先安装 Deno：https://deno.com/'
  read -r -p '按回车退出。' ignored
  exit 1
fi
if [ ! -x .venv/bin/python ]; then
  "$relay_python" -m venv .venv
  .venv/bin/python -m pip install -r requirements.txt
fi
relay_args=(--bind 0.0.0.0)
if [ -n "${SPACE_RELAY_PROXY:-}" ]; then relay_args+=(--proxy "$SPACE_RELAY_PROXY"); fi
if [ -n "${SPACE_SOURCE_URL:-}" ]; then relay_args+=(--source "$SPACE_SOURCE_URL"); fi
printf '%s\n' '太空窗中转已启动；请保持此窗口和 Mac 运行。按 Ctrl+C 停止。'
exec .venv/bin/python space_relay.py "${relay_args[@]}"
