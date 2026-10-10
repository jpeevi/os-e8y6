#!/bin/sh
# The browser is the workspace. JWM supplies only window management and shortcuts.
exec dbus-run-session -- jwm -f "$HOME/.jwmrc"
