# Interactive login profile for os:e8y6.
if [ -n "${BASH_VERSION:-}" ] && [ -f "$HOME/.bashrc" ]; then
  . "$HOME/.bashrc"
fi
if [ "$(tty 2>/dev/null)" = /dev/tty1 ] && [ -z "${DISPLAY:-}" ] && [ -z "${SSH_CONNECTION:-}" ]; then
  exec startx
fi
