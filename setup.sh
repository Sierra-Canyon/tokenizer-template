#!/bin/bash
# Honors Software Engineering — one-time setup for this repository.
# Run it once, from the top of the repo:  ./setup.sh
set -e
cd "$(dirname "$0")"

echo "==> Python 3.12 and dependencies"
uv python install 3.12
uv sync

echo
echo "==> git filter: strip notebook output before it reaches a commit"
# Without this, one re-run of a notebook shows up as 4,000 changed lines and your
# reviewer cannot see the twelve you actually wrote. The filter rewrites the blob
# on the way into the index; your local file keeps its output.
git config filter.nbstrip.clean \
  "uv run python -c \"import sys,json; d=json.load(sys.stdin); [c.update(outputs=[],execution_count=None) for c in d['cells'] if c['cell_type']=='code']; json.dump(d,sys.stdout,indent=1); sys.stdout.write('\n')\""
git config filter.nbstrip.smudge cat
git config filter.nbstrip.required true

echo
echo "==> secret guard"
chmod +x scripts/install_secret_guard.sh
./scripts/install_secret_guard.sh

echo
echo "==> environment check"
uv run scripts/check_env.py || true

cat <<'EOF'

Setup done. Two things to verify yourself, because a filter that silently did not
install is worse than no filter:

  1. Open notebooks/01_tokenizer_probe.ipynb, run one cell, save it, then:
         git diff --stat
     You should see your source change and NOT thousands of output lines.

  2. Try to commit a fake key and watch it get rejected:
         echo 'sk-test1234567890abcdefghijklmnopqrstuvwxyz' > /tmp/leak.txt
         cp /tmp/leak.txt . && git add leak.txt && git commit -m "should fail"
     Then: rm leak.txt && git reset

EOF
