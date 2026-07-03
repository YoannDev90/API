#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

ENDPOINTS_MD="ENDPOINTS.md"

# ── Generate EP table ────────────────────────────────────────────────────
{
  echo "# Endpoints"
  echo
  echo "Auto-generated. Run \`scripts/generate_docs.sh\` to refresh."
  echo
  echo "| Method | Path | File |"
  echo "|--------|------|------|"
} > "$ENDPOINTS_MD"

find endpoints -name '*.py' ! -name '__init__.py' -print | sort | while read -r file; do
  name=$(echo "$file" | sed 's|^endpoints/||' | sed 's|\.py$||' | tr '/' '.')
  while IFS=: read -r line; do
    method=$(echo "$line" | sed -n 's/.*@router\.\([a-z]*\)(.*/\1/p')
    path=$(echo "$line" | sed -n "s/.*@router\.$method(\"\([^\"]*\)\".*/\1/p")
    [ -n "$method" ] && [ -n "$path" ] && echo "| $method | $path | $name.py |"
  done < <(grep -E '@router\.(get|post|put|delete|patch|api_route)\(' "$file" 2>/dev/null || true)
done >> "$ENDPOINTS_MD"

# sort by path (keep header rows at top)
HEADER_LINES=6
BODY=$(tail -n +$((HEADER_LINES+1)) "$ENDPOINTS_MD" | sort -t'|' -k3)
{ sed -n "1,${HEADER_LINES}p" "$ENDPOINTS_MD"; echo "$BODY"; } > "$ENDPOINTS_MD.tmp" && mv "$ENDPOINTS_MD.tmp" "$ENDPOINTS_MD"

COUNT=$(tail -n +5 "$ENDPOINTS_MD" | wc -l)
echo "| **${COUNT} routes** | | |" >> "$ENDPOINTS_MD"
echo "→ $ENDPOINTS_MD ($COUNT routes)"

# ── Update README tree ───────────────────────────────────────────────────
TREE=$(mktemp)
ENDCOUNT=$(find endpoints -name '*.py' ! -name '__init__.py' | wc -l)
SUBDIRS=$(find endpoints -mindepth 1 -maxdepth 1 -type d | sort | sed 's|endpoints/||')
TREE_CONTENT="├── app.py
├── config.py
├── keep_alive.py
├── main.py
├── proxy.py
├── user_agents.json
├── .env.example
├── requirements.txt
├── pyproject.toml
├── uv.lock
├── ENDPOINTS.md
├── scripts/
├── tests/
├── .github/
└── endpoints/   (${ENDCOUNT} files)"
for d in $SUBDIRS; do
    count=$(find "endpoints/$d" -name '*.py' ! -name '__init__.py' | wc -l)
    TREE_CONTENT="$TREE_CONTENT
    ├── $d/   (${count} files)"
done

cat > "$TREE" <<TREEBLOCK
\`\`\`
${TREE_CONTENT}
\`\`\`
TREEBLOCK

# replace tree block in README (first ``` block after "## Structure")
awk -v tree="$(cat "$TREE")" '
  /^## Structure/ { found=1 }
  /^```$/ && found && !inside {
    print tree; inside=1; next
  }
  /^```$/ && inside { inside=0; found=0; next }
  !inside { print }
' README.md > README.tmp && mv README.tmp README.md

rm "$TREE"
echo "→ README.md updated"
