# Bravium development instructions

- OS: os:e8y6 (Bravium) v0.8.9, Ubuntu 26.04 amd64 base.
- Product philosophy: Brave **is** the desktop. JWM is invisible; no panel, dock or Xfce.
- Browser starts once. QTerminal via Ctrl+Alt+T; installer only via `bravium-install` in a terminal.
- Build only in an isolated rootfs. Never change firewall, packages or desktop settings on the Xubuntu host.
- VM-only Calamares prototype: disposable QEMU/KVM virtual disks. Never run installer on a physical disk.
- No UFW by default; optional utilities can be installed by administrators via APT. Preserve security updates.
- zram defaults to half RAM, zstd, priority 100. Keep adequate website font fallbacks.
- Never claim a successful ISO boot or installation until verified on a real QEMU run.
- Run `./build.sh check` and `python3 -m unittest discover -s tests -v`.
- Only README.md, AGENTS.md and LICENSE as root documentation.
- Before writing code for future updates, confirm plan with the user.
- Do not commit build products, logs, VM disks, secrets or credentials.
