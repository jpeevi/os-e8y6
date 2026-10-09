Brave web app launchers are discovered at login from ~/.local/share/applications/brave-*.desktop.
Newly installed apps appear after logging out and back in, or after running
`barvium-webapp-menu && jwm -restart`.
The main Brave window's skip-taskbar hint is best-effort; must be checked under QEMU.
The live ISO is ephemeral: web apps are lost after reboot without persistence.
