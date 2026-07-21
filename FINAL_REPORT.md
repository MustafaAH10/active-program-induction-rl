# SkyFoundry final report

Date: 2026-07-22  
Status: Definition of Done met; no required external blocker remains.

## Implemented

SkyFoundry is a working browser construction studio, not a static mockup. Submitting the default brief starts an empty scene and stages seven typed, validated Building DSL actions into a deterministic Manhattan tower projection. The studio contains 1,764 stable logical components, 118 dependency-checked tasks, eight visible scripted agent rounds, and all ten construction phases.

The Three.js/R3F experience provides orbit, pan, zoom, six canonical cameras, realistic/clay/structure/x-ray/night modes, Manhattan-like local context, selection, focus, per-system and per-component visibility, instanced structure/façade/site systems, crane motion, workers, vehicles, excavation, public realm, and absolute-tick construction animation. The timeline supports pause, resume, scrub, speed, phase stepping, and replay.

The canonical write boundary is the strict Zod Building DSL action log. Sequential semantic validation checks schemas, generators/materials, provenance, dependencies, duplicate IDs, dimensions, counts, project budgets, and task DAGs before the pure reducer derives a scene. Revisions use the same boundary: the crown request is parsed, previewed with validation results, approved into a stable-ID update action, animated, and undoable.

The companion FastAPI application implements Pydantic contracts, a scripted LangGraph workflow, SQLite persistence, SSE events, actions/tasks/artifact endpoints, and provider status. Its operation union is strict and rejects arbitrary operation shapes. The credential-free browser stages the same deterministic scripted action fixture locally, so the base demo does not depend on the Python server.

Exports include complete project JSON (with action log), scene JSON, timeline JSON, and a canvas PNG. The Playwright screenshot loop records the canonical cameras/states. A provider-neutral TypeScript client includes replay and credential-gated OpenAI-compatible adapters.

The optional CAD path accepts a checked-in dimensional planter recipe only. A resource-limited temporary subprocess produces STEP, STL, and GLB through trusted CadQuery operations; the checked-in 7,288-byte GLB is represented by a typed DSL component and verified inside the live Three.js scene. No raw Python/CadQuery source field exists. TRELLIS was not installed.

## Run

```bash
cd /home/mustafaah/allbench
pnpm install --frozen-lockfile
python3 -m venv --prompt allbench .venv
.venv/bin/pip install -r apps/orchestrator/requirements.txt
pnpm demo:seed
pnpm dev
```

Open `http://localhost:3000` and submit the prefilled brief.

Optional orchestrator:

```bash
PYTHONPATH=apps/orchestrator .venv/bin/uvicorn skyfoundry.main:app --host 127.0.0.1 --port 8000
```

Optional CAD regeneration:

```bash
.venv/bin/pip install -r apps/cad-worker/requirements-optional.txt
.venv/bin/python apps/cad-worker/runner.py apps/cad-worker/planter-recipe.json --output artifacts/cad-planter
```

## Exact final verification

| Command | Result |
| --- | --- |
| `pnpm install --frozen-lockfile` | Passed; nine workspaces, lockfile current, 611 ms |
| `pnpm demo:seed` | Passed; 1,764 components, 118 tasks, seven actions |
| `pnpm validate:project` | Passed; seven idempotent actions, sequence seven |
| `pnpm lint` | Passed; workspace TypeScript checks and web ESLint, zero warnings |
| `pnpm typecheck` | Passed across eight source workspaces |
| `pnpm test` | Passed; 15 TypeScript tests and six Python tests in the final suite |
| `pnpm build` | Passed; four static Next.js routes, 103 kB shared first load |
| `pnpm test:e2e` | Passed; two Chromium scenarios in 31.2 s |
| `pnpm audit --prod` | Passed; no known vulnerabilities |
| CAD runner command above | Passed; STEP 30,868 B, STL 17,484 B, GLB 7,288 B |
| Uvicorn + `curl /health` and `/api/providers` | Passed; HTTP 200, scripted active, optional providers disabled |

The Python suite emits one upstream `LangChainPendingDeprecationWarning` about a future checkpoint serializer default; it does not affect behavior or test status. The browser suite checks for console/page errors and found none. It additionally verifies the empty-to-seven-patch transition, live renderer/context, imported CAD object, all agent cards, timeline playback, inspector provenance, revision/undo, replay, parsed project export content, and PNG download.

## Screenshots

- `screenshots/01-landing.png` — credential-free landing and default brief
- `screenshots/02-foundation.png` — early construction
- `screenshots/03-structure.png` — frame sequence
- `screenshots/04-completed-daylight.png` — completed overview
- `screenshots/05-section-inspector.png` — Section X and column provenance
- `screenshots/06-revised-crown.png` — approved crown revision
- `screenshots/07-completed-night.png` — night lighting
- `screenshots/08-mobile-viewer.png` — 390 × 844 responsive viewer

## Architecture and review outcomes

The action log is canonical; Three.js is a derived projection and cannot be mutated by agent code. Zustand owns browser interaction and absolute timeline state. Pure packages own schemas, validation, procedural descriptors, tasks, and deterministic fixtures. FastAPI/LangGraph is an optional orchestration service, and external model/CAD/asset services sit behind disabled-by-default adapters.

Read-only subagent reviews covered architecture, Three.js performance, browser QA, security, and tests. Their findings drove the validated write gateway, stricter Python operation union, staged product loop, removal of remote HDR and unstable Rapier initialization from the critical path, batched Manhattan context, reduced draw calls, responsive drawers, corrected section/camera behavior, stronger exports, and adversarial/E2E coverage. The final security re-review found no critical issue; the final test re-review found no remaining Definition-of-Done blocker.

## Provider status

- Scripted agents: implemented and default; no credentials.
- OpenAI-compatible multimodal adapter: implemented behind explicit HTTPS/localhost configuration, response cap, timeout/budget settings, and output revalidation; not exercised without credentials.
- CadQuery: optional dependencies exercised locally; strict recipe and subprocess path implemented. Base install remains independent.
- TRELLIS: disabled protocol/mock/local-folder interfaces only; not downloaded or installed.
- OSM: disabled. The demo uses original local stylized context.

## Performance observations

At the completed daylight state in 1440 × 900 headless Chromium: WebGL context healthy, 42 draw calls, 26,852 triangles, 42 geometries, zero textures, device pixel ratio 1, and 0.7 ms for an explicit renderer call. A two-second browser `requestAnimationFrame` sample yielded 36 callbacks/s under the available software-rendered headless environment. Demand rendering, 30 Hz UI tick throttling, instancing, no remote environment maps, and no permanent screenshot buffer keep the interaction usable. This is evidence for the test host, not a claim about production laptop-GPU frame rate.

## Limitations

- The local browser experience and Python LangGraph service are separately deployable; a production version should stream the server SSE state directly into the web agent panel.
- Live multimodal behavior was not exercised because no credentials were required or available.
- Whole-building GLB export is not enabled; project/scene/timeline JSON and PNG are the supported base exports. The optional CAD part does export GLB.
- Rapier remains available as an optional dependency but is outside the critical path after it caused WebGL context loss under Chrome/SwiftShader. Construction motion is deterministic/keyframed rather than physically simulated.
- CAD isolation uses a separate temporary subprocess, socket denial, and resource limits. Production should add a no-network container or OS namespace.
- Hardware-GPU, Safari, and Firefox performance were not measured in this environment.

## Next five highest-value improvements

1. Connect the web session to FastAPI SSE so streamed LangGraph rounds and browser patches share one persisted run.
2. Profile on representative laptop/mobile GPUs and add distance-based façade/worker/vehicle/crane LOD where measurements justify it.
3. Add a containerized CAD service with kernel-level network isolation, artifact signing, and browser-side mesh-budget validation.
4. Add a real credential-gated multimodal provider evaluation with structured-output repair telemetry and visual regression scoring.
5. Add whole-scene GLB packaging plus optional, licensed OSM context ingestion; keep TRELLIS decorative and separately deployed.

## Blocked items

No Definition-of-Done item is blocked. Live provider evaluation needs user-supplied credentials, and production TRELLIS/OSM services are intentionally outside the credential-free MVP. The remote `playwright-interactive` skill named in the request was not installed in the available skill catalog, so browser QA used the repository's direct Playwright integration instead.
