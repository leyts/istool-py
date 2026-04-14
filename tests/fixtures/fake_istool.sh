#!/usr/bin/env bash
# Records argv to stdout with shell-safe quoting, optional stderr,
# exits with chosen code. Controlled via env vars so tests don't have
# to patch the script.

LINE="argv:"

for arg in "$@"; do
    LINE+=" $(printf '%q' "$arg")"
done

printf '%s\n' "$LINE"

if [[ -n "$FAKE_ISTOOL_STDERR" ]]; then
    printf '%s\n' "$FAKE_ISTOOL_STDERR" >&2
fi
if [[ -n "$FAKE_ISTOOL_SLEEP" ]]; then
    sleep "$FAKE_ISTOOL_SLEEP"
fi

exit "${FAKE_ISTOOL_EXIT_CODE:-0}"
