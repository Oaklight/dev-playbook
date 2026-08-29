#!/bin/sh

# ── PROJECT-SPECIFIC: change binary path ──
BINARY="/usr/local/bin/my-tool"

# Prepend binary path if first arg starts with "-"
if [ "${1#-}" != "$1" ]; then
	set -- "$BINARY" "$@"
fi

exec "$@"
