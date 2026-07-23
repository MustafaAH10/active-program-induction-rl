# SkyFoundry

SkyFoundry is a browser-first, deterministic 3D construction studio. Enter a tower brief, configure a named architecture/civil/construction crew, watch it reach weighted consensus through schema-validated Building DSL actions, scrub a ten-phase construction sequence, inspect or reversibly demolish individual components, preview a scoped crown revision, and export the project or a screenshot.

> Conceptual simulation only. Not architectural, structural, construction, zoning, or safety advice.

## Quick start

Prerequisites: Node 20+, pnpm 10+, Python 3.11+ and Chrome.

```bash
pnpm install
python3 -m venv --prompt allbench .venv
.venv/bin/pip install -r apps/orchestrator/requirements.txt
pnpm demo:seed
pnpm dev
```

Open <http://localhost:3000>. No API key, GPU, live map service, or CAD installation is required.

Run the optional orchestrator separately:

```bash
pnpm dev:orchestrator
```

The launcher reads the ignored root `.env` when present. Hosted deployments should
provide the same values through their environment-variable settings.

## Verification

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm build
pnpm test:e2e
pnpm test:visual
pnpm validate:project
```

The default build is derived from seven versioned DSL actions and contains 1,764 stable logical components, 118 absolute-tick construction tasks, eight visible agent rounds, and all ten required phases. Repeated façade, structure, worker, foundation, and landscape systems use instanced rendering while retaining logical selection IDs. One public-realm planter demonstrates the optional trusted CadQuery recipe → GLB → browser import path.

## What is optional

- `ENABLE_LIVE_AGENTS=false`: the OpenAI Responses API adapter is server-gated and the default provider is scripted. Live project crews can choose `gpt-5.4-nano` or `gpt-5.6-luna`; keys never belong in browser state or source control.
- `ENABLE_CAD_WORKER=false`: only strict dimensional CAD recipes are accepted; unrestricted Python is never executed. CadQuery is not installed by default.
- `ENABLE_TRELLIS=false`: the protocol adapter is documented and disabled. TRELLIS is not downloaded.
- `ENABLE_OSM_IMPORT=false`: the Manhattan-like block is an original local fixture; runtime map access is unnecessary.

See [ARCHITECTURE.md](ARCHITECTURE.md), [SAFETY.md](SAFETY.md), [PROGRESS.md](PROGRESS.md), and [FINAL_REPORT.md](FINAL_REPORT.md).
