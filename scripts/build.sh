#!/usr/bin/env bash
# Сборка сайта в dist/. Ничего не коммитит и не публикует.
set -Eeuo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

NOTEPUB_REF="${NOTEPUB_REF:-8ef36a58c94dca5bd7f3f696c05a9201cd140d47}"   # тот же, что у site/ и в .github/workflows/pages.yml
NOTEPUB_BIN="${NOTEPUB_BIN:-}"
if [[ -z "$NOTEPUB_BIN" ]]; then
  if [[ -x "$ROOT_DIR/.bin/notepub" ]]; then NOTEPUB_BIN="$ROOT_DIR/.bin/notepub"
  elif [[ -x "$ROOT_DIR/../site/.bin/notepub" ]]; then NOTEPUB_BIN="$ROOT_DIR/../site/.bin/notepub"
  elif command -v notepub >/dev/null 2>&1; then NOTEPUB_BIN="$(command -v notepub)"
  else
    command -v go >/dev/null 2>&1 || { echo "Ошибка: не найден notepub и не установлен Go." >&2; exit 1; }
    mkdir -p "$ROOT_DIR/.bin"
    GOBIN="$ROOT_DIR/.bin" go install "github.com/cookiespooky/notepub/cmd/notepub@${NOTEPUB_REF}"
    NOTEPUB_BIN="$ROOT_DIR/.bin/notepub"
  fi
fi

CONFIG="${CONFIG:-./config.yaml}"; DIST="${DIST:-./dist}"
echo "Сайт ($CONFIG -> $DIST)"
rm -rf "$DIST" .notepub
mkdir -p "$DIST"
"$NOTEPUB_BIN" validate --config "$CONFIG" --rules ./rules.yaml
"$NOTEPUB_BIN" index --config "$CONFIG" --rules ./rules.yaml
"$NOTEPUB_BIN" validate --config "$CONFIG" --rules ./rules.yaml --resolve ./.notepub/artifacts/resolve.json --links --markdown
"$NOTEPUB_BIN" build --config "$CONFIG" --rules ./rules.yaml --dist "$DIST" --artifacts ./.notepub/artifacts
touch "$DIST/.nojekyll"
cp theme/assets/favicon.ico "$DIST/favicon.ico"   # Яндекс и старые браузеры спрашивают /favicon.ico в корне
[[ "$CONFIG" == "./config.yaml" ]] && echo "veralozhkina.ru" > "$DIST/CNAME"
echo "Готово: $DIST — не закоммичено и не опубликовано"
