# SkyFoundry

SkyFoundry is a browser-first, deterministic 3D construction studio. Enter a tower brief, watch a scripted architecture team produce schema-validated Building DSL actions, scrub a ten-phase construction sequence, inspect individual instanced components, preview a scoped crown revision, and export the project or a screenshot.

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
PYTHONPATH=apps/orchestrator .venv/bin/uvicorn skyfoundry.main:app --port 8000
```

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

- `ENABLE_LIVE_AGENTS=false`: an OpenAI-compatible provider interface exists, but the default provider is scripted.
- `ENABLE_CAD_WORKER=false`: only strict dimensional CAD recipes are accepted; unrestricted Python is never executed. CadQuery is not installed by default.
- `ENABLE_TRELLIS=false`: the protocol adapter is documented and disabled. TRELLIS is not downloaded.
- `ENABLE_OSM_IMPORT=false`: the Manhattan-like block is an original local fixture; runtime map access is unnecessary.

See [ARCHITECTURE.md](ARCHITECTURE.md), [SAFETY.md](SAFETY.md), [PROGRESS.md](PROGRESS.md), and [FINAL_REPORT.md](FINAL_REPORT.md).
