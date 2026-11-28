#!/usr/bin/env bash
# Runs every test suite and prints each suite's score plus any failures.
# Needs Python 3, Playwright and Chrome at /usr/bin/google-chrome.
# The "plain: no JS errors" check in run.py fails offline (font and favicon can't load); that's expected.
cd "$(dirname "$0")"
for t in run exp ux2 img results weekres lanes help brief activity invshare v8 next staging video runes newweek uploads mystnames mystlings gear builds presets editshots dock presetorder resreader opproster; do
  out=$(timeout 400 python3 "$t.py" 2>&1)
  printf '== %s: %s\n' "$t" "$(echo "$out" | grep -E '^ *[0-9]+ ?/ ?[0-9]+( passed)?$' | tail -1)"
  echo "$out" | grep -E '^FAIL|Error' | head -5
done
