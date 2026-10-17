# os:e8y6 development instructions

## Project identity

- Product: os:e8y6.
- Current release: v0.8.19.
- Base: Ubuntu 26.04 amd64.
- Status: experimental browser-first operating system.
- Primary interface: browser:e8y6, derived from KDE Falkon and Qt WebEngine.
- Window manager: JWM.
- No conventional desktop panel, dock, or Xfce environment.
- The operating system and browser use independent version numbers.
- Do not reintroduce retired product branding.

## Desktop and session

- browser:e8y6 is the primary graphical OS interface.
- Keep the browser maximized and borderless through JWM.
- Preserve the existing browser window restrictions.
- Browser recovery is handled through `e8y6-session`.
- Use process-exit-driven recovery rather than continuous polling.
- Avoid rapid browser restart loops.
- Preserve QTerminal access through Ctrl+Alt+T.
- Preserve the graphical power menu through Alt+F4.
- Preserve screen locking through Super+L.
- Do not introduce a conventional desktop environment without explicit user approval.
- Maintain access to networking and recovery utilities.

## Installer safety

- Calamares is experimental and VM-restricted.
- The supported installation launcher is `e8y6-install`.
- Installation is restricted to disposable QEMU/KVM virtual disks.
- Never run the installer on physical disks or host partitions.
- Preserve checks for virtualization, Casper live boot, and interactive terminal access.
- Require explicit installer confirmation.
- Never bypass installer safety checks for convenience.
- Treat failed installations as potentially destructive to the test virtual disk.
- Preserve installer logging and error reporting.
- Maintain required partitioning, filesystem, GRUB, initramfs, and installed-session integration.

## Build isolation

- Build only inside an isolated root filesystem or designated project build environment.
- Do not unintentionally change host firewall rules, packages, or desktop settings.
- Keep build outputs inside designated project directories.
- Inspect existing mounts before cleanup or rebuilding.
- Do not manipulate physical disk partitions during tests.
- Preserve reproducible ISO and package build procedures.

## Security and dependencies

- UFW is not included as a default firewall.
- Optional utilities may be installed by administrators using APT.
- Preserve security updates and unattended-upgrades.
- Maintain NetworkManager functionality.
- Preserve zram defaults: half RAM, zstd, priority 100.
- Keep suitable multilingual font fallbacks for websites.
- Do not arbitrarily remove dependency packages to reduce ISO size.
- Treat JWM window restrictions as user-interface behavior, not security controls.

## Browser integration

- browser:e8y6 is the default browser and OS interface.
- Use the version pinned in `packages/browser-e8y6.lock`.
- Verify downloaded browser packages against their recorded SHA-256 checksums.
- Do not silently substitute unpinned browser builds.
- Do not reintroduce Brave as the OS interface.
- Preserve browser startup, JWM window matching, and session recovery.
- Test browser updates in a freshly built ISO.
- Preserve browser profile compatibility wherever possible.
- Do not claim browser integration is verified without runtime testing.

## Testing

Run source validation before committing changes:

```sh
./build.sh check
python3 -m unittest discover -s tests -v
```

Inspect existing build mounts before building an ISO.

For installed-system changes, test clean installation in QEMU/KVM.

Verify independent boot without the live ISO.

Verify networking, browser startup, terminal access, and persistence after reboot.

Use separate disposable virtual disks for clean-install and dual-boot testing.

Never claim successful ISO boot, installation, persistence, or dual-boot without verification in the relevant QEMU environment.

Clearly distinguish source-level testing from runtime verification.

## Documentation and workflow

- Keep README.md aligned with the current release.
- Keep AGENTS.md focused on development rules.
- Only README.md, AGENTS.md, and LICENSE should be root documentation files.
- Before implementing future code changes, confirm the plan with the user.
- Work incrementally, with one step or shell command at a time.
- Verify changes before proceeding.
- Preserve existing functionality unless changes are explicitly approved.
- Do not commit build products, logs, VM disks, secrets, credentials, or temporary files.
- Avoid committing generated artifacts unless they are intentionally tracked project assets.
- Do not invent features, test results, or release claims.

## Release management

- Maintain consistent OS version references across configuration, branding, and documentation.
- Keep browser versions independent from OS versions.
- Run source validation before committing releases.
- Build and test release ISOs in an isolated environment.
- Verify browser package integrity.
- Document known limitations and outstanding work in README.md.
- Preserve experimental installation safety restrictions.
- Do not describe the project as production-ready until the required acceptance tests have passed.

## v0.8.19 status and outstanding acceptance checks

- Explicit logout signaling is implemented but requires QEMU verification for clean Qt profile shutdown.
- `e8y6-debug` is local/read-only and must not collect cookies, passwords or private browser data.
- CLI lock screen matching the exact Linux login console typography is **not yet implemented**; retaining secure PAM-backed locking takes priority over an unsafe imitation.
- Window opening jitter may require Qt application-side geometry or compositor work. JWM maximization rules alone do not guarantee no initial resize.
- Latest stable browser release must be independently verified before the next ISO build; do not silently keep an old pin or adopt unverified release artifacts.
