# Barvium install counter (opt-in only)

The client is intentionally **not** configured to start automatically; no systemd service or timer is enabled. After a *future installer* completes and the user explicitly opts in, that installer could call `client.py --consent --endpoint https://your-server.example --version 0.3.0-dev`. Until the installer is implemented, this command is only for voluntary manual demonstrations and must not be used as proof of an installed OS.

Payload contains only `event` and `version`, not a per-install ID. An on-disk marker stops repeat submissions on the same home directory after a successful HTTP response. It isn't a security measure: reinstalls, restored home directories, and manual calls can cause duplicates. Therefore server counts are **reported events**, not unique devices or precise installation totals.

The server necessarily receives a source IP at network level; application code does not store it. Reverse proxy, load balancer, CDN and hosting logs must also be configured accordingly. There is no analytics without consent and no background retries.
