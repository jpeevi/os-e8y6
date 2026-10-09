# Barvium privacy policy — development draft

Barvium aims to remove optional reporting components inherited from Ubuntu and disable optional Brave analytics after verifying the supported browser policy/settings. Security-critical browser and OS update traffic may still occur. No claim of fully zero telemetry or zero network access is made until an image has been built and independently audited.

**Installation reporting defaults to OFF.** If you explicitly choose to report an installation, Barvium sends one HTTPS request containing only an event name (`install_completed`) and Barvium version. No serial numbers, machine IDs, account details, file names, browsing history, or persistent network identifiers are included. An on-disk local marker tries to prevent repeat reporting. The remote server can still observe your public IP during the connection, and network infrastructure may retain logs outside Barvium's control.

The event can be skipped without limiting functionality. Since the server stores only aggregate event counts and not individual identities, a previously reported event cannot be identified and selectively erased. Our current project contains only scaffolding; the feature is **not** installed or enabled automatically. This draft must be updated with the deployment host, contact information and true operational practices before release.
