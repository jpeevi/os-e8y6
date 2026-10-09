#!/bin/sh
# No display manager; JWM controls windows, Tint2 owns the visible top bar.
exec dbus-run-session -- /usr/local/bin/barvium-session
