#!/bin/bash
# rerun: bash docs/records/gart-H3/run.sh [--own]
H=$(cd "$(dirname "$0")" && pwd)/harness.py
while read repo pkg mod; do
  echo "=== $pkg ($repo)"; (cd "$repo" && python3 -I "$H" "$repo" "$pkg" "$mod" "$@" 2>&1)
done <<L
/home/user/galivelop-developer gdev schema
/home/user/zeldris/galivelop-image-generator gimg schema
/home/user/zeldris/galivelop-voice-generator gvoice schema
/home/user/galivelop-client-catcher opportunity_intel schema
L
