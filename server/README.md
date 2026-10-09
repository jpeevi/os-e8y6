# Install counter server

Not deployed: the owner has no server/domain yet. This is a development-only receiver. It uses FastAPI and SQLite for aggregate event counts only (no machine identifiers, client IP, timestamps or individual event records). Do not expose it directly to the public internet without TLS reverse proxy and rate limiting; unauthenticated counters can be inflated with fake reports.

For local testing in a disposable Python environment, install `requirements.txt`, run `uvicorn app:app --host 127.0.0.1 --port 8000 --no-access-log` from `server/`, and send test events using a local HTTP client. The actual Barvium reporter **requires HTTPS** and explicit consent.

For production, disable access logs and request-body logging at every layer (reverse proxy, CDN, host), configure TLS, apply rate limiting and authentication or abuse protection appropriate to the threat model, and publish a privacy notice. A proxy commonly sees IP addresses even if this app does not record them. Back up the SQLite database and plan a retention policy. No deployment or network activity happens during project staging.
