# Privacy configuration

`remove-optional-reporting-chroot.sh` is **not** intended for the Xubuntu development computer. It requires an explicit `/etc/barvium-build-rootfs` marker *inside* an isolated build root filesystem. It removes installed `ubuntu-report`, `ubuntu-insights`, `whoopsie`, `apport`, and `popularity-contest` packages when present, and sets `/etc/default/apport` to disabled. Review dependency consequences during the actual ISO build; this is not a guarantee of zero network traffic.

Brave's P3A reporting can be switched off using the browser's **Settings → Privacy and security** controls. Brave policies vary by version and require verification before we automatically enforce them. Browser crash uploads, update checks, Safe Browsing, and other network activity are distinct; avoiding optional analytics must not disable essential security protections.

We do not install or enable the Barvium install counter by default. Reporting is optional and initiated only after a user chooses to opt in; see `telemetry/README.md`.
