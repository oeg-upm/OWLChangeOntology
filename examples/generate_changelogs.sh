#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
GENERATOR="$REPO_DIR/tools/och2changelog.py"
PYTHON="${PYTHON:-python3}"
MODE="html"

usage() {
  cat <<'EOF'
Usage: examples/generate_changelogs.sh [--html|--markdown|--all]

Generate changelogs for every examples/*/*_changelog.ttl file.

  --html      Generate *_changelog-searchable.html files (default)
  --markdown  Generate CHANGELOG.md files
  --all       Generate both HTML and Markdown

Set PYTHON to choose a different Python interpreter.
EOF
}

case "${1:-}" in
  ""|--html)
    MODE="html"
    ;;
  --markdown)
    MODE="markdown"
    ;;
  --all)
    MODE="all"
    ;;
  -h|--help)
    usage
    exit 0
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac

if [[ ! -f "$GENERATOR" ]]; then
  echo "Generator not found: $GENERATOR" >&2
  exit 1
fi

shopt -s nullglob
inputs=("$SCRIPT_DIR"/*/*_changelog.ttl)

if [[ ${#inputs[@]} -eq 0 ]]; then
  echo "No *_changelog.ttl files found under $SCRIPT_DIR" >&2
  exit 1
fi

for input in "${inputs[@]}"; do
  example_dir="$(dirname "$input")"
  example_name="$(basename "$example_dir")"
  title="$example_name ontological changelog"

  if [[ "$MODE" == "html" || "$MODE" == "all" ]]; then
    html_output="${input%.ttl}-searchable.html"
    "$PYTHON" "$GENERATOR" "$input" \
      --output "$html_output" \
      --output-format html \
      --title "$title"
  fi

  if [[ "$MODE" == "markdown" || "$MODE" == "all" ]]; then
    markdown_output="$example_dir/CHANGELOG.md"
    "$PYTHON" "$GENERATOR" "$input" \
      --output "$markdown_output" \
      --output-format markdown \
      --title "$title"
  fi
done

echo "Generated changelogs for ${#inputs[@]} example graphs."
