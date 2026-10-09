# Development instructions for AI coding assistants

- OS identity: `os:e8y6`, codename `Bravium`, current release `0.8`; Ubuntu 26.04 (`resolute`) amd64 base.
- Do not modify, purge or change firewall settings on the Xubuntu build host; all OS changes belong in isolated ISO rootfs.
- Preserve Brave-first JWM + Tint2 with PCManFM, QTerminal and independent Brave web apps.
- Preserve opt-in-only install telemetry and avoid collecting device/user identifiers.
- Never run Calamares outside disposable QEMU/KVM test VMs. Always require disk choice and confirmation; do not automate destructive partitioning.
- Never claim an ISO boots, installs, preserves dual-boot or supports real hardware without corresponding test evidence.
- Keep CLI login, standard-user restrictions and account setup reserved for the v0.9 milestone; do not falsely claim v0.8 provides them.
- Keep only root `README.md`, `AGENTS.md`, `LICENSE` for prose documentation. Maintain release details in README, not per-version Markdown files.
- Before proposing code, describe the plan and obtain explicit user approval.
- Run `./build.sh check` and `python3 -m unittest discover -s tests -v`; where possible test builds using disposable VM disks.
- Do not commit `dist/`, `work/`, `out/`, generated ISOs, secrets, logs, host paths or user data.
