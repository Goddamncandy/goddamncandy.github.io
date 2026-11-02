#!/usr/bin/env bash
# Посмотреть сайт у себя: собрать с локальными адресами в dist-dev/ и открыть на http://127.0.0.1:8089/
set -Eeuo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
CONFIG=./config.dev.yaml DIST=./dist-dev scripts/build.sh
echo "http://127.0.0.1:8089/ — Ctrl+C, чтобы остановить"
[[ "${1:-}" == "--build-only" ]] || python3 -m http.server 8089 --bind 127.0.0.1 --directory dist-dev
