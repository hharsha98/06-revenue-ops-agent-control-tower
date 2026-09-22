# Contabo / sslip notes

This file is a runbook for **this** repository. It does not deploy anything, and it
does not claim a public URL.

Agent Fleet, AgentOps Studio, Agent OS, and the RAG lab are different products.
Do not point RevenueOps Control Tower at their hosts, and do not publish this
product on their ports.

## Ports

| Port | Use on a shared VPS |
|---|---|
| **8060** | This product. One process serves the API, `/health`, and the built UI. |
| **3066** | Optional Vite dev server, or the optional Compose frontend container. |
| 8000, 3002 | Reserved for Agent Fleet. Do not bind this app here. |
| 8402 | Reserved for the RAG lab. |
| 8090 | Reserved for Agent OS. |
| 8010, 3010 | Reserved for AgentOps Studio. |

Postgres `5432` and Redis `6379` are only for optional Compose. The native demo
does not listen on them.

## Process

```bash
cd /opt/revenueops-control-tower
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
cd frontend && npm ci && npm run build && cd ..
HOST=0.0.0.0 PORT=8060 .venv/bin/python -m backend.app
```

`/health` returns `product=revenueops-control-tower`, `host`, and `port`.

A visitor opens `http://YOUR_IP:8060`. Replace `YOUR_IP` with the address of the
machine that is actually running **this** repo.

## Example systemd unit

```ini
[Service]
WorkingDirectory=/opt/revenueops-control-tower
Environment=HOST=0.0.0.0
Environment=PORT=8060
Environment=AUTONOMY_MODE=sandbox
ExecStart=/opt/revenueops-control-tower/.venv/bin/python -m backend.app
Restart=on-failure
```

Do not put API keys, OAuth tokens, or cloud credentials in the unit. This demo
runs without them.

## Example sslip reverse proxy

Use a hostname that belongs to this service, not to another portfolio app:

```
revenueops.YOUR_IP.sslip.io {
  reverse_proxy 127.0.0.1:8060
}
```

`YOUR_IP` is a placeholder. Caddy or any other reverse proxy is optional.
No Cloudflare paid plan and no R2 bucket are required.

Promote the studio card from **Early** to **Live** only after that hostname
answers `/health` with `revenueops-control-tower`.
