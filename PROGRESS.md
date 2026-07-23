# SkyFoundry progress

Last updated: 2026-07-23

## Current status

The deterministic Manhattan Tower MVP and the 2026-07-23 product-polish iteration meet their completion criteria. The app now includes configurable multi-agent consensus, a server-gated live provider, richer Manhattan context, and reversible sandbox destruction. The repository is a pnpm workspace and the Python environment `.venv` uses the prompt `allbench`.

## Milestones

- [x] M0 — pnpm monorepo, commands, docs, tests, landing page, deterministic fixture
- [x] M1 — R3F Manhattan sandbox, context, roads, orbit controls, modes, camera rigs, selection
- [x] M2 — strict Building DSL, reducer, validation, generators, materials, stable IDs, instancing
- [x] M3 — 118-task DAG, ten phases, absolute-tick animation, crane/workers/vehicles, timeline controls
- [x] M4 — FastAPI/LangGraph/SQLite/SSE scripted agent studio with eight visible rounds
- [x] M5 — deterministic browser capture command and canonical Playwright screenshot loop
- [x] M6 — provider-neutral protocol, replay provider, and credential-gated OpenAI-compatible TS adapter
- [x] M7 — scoped crown parser, validation preview, approval animation, stable-ID update, undo
- [x] M8 — strict CAD recipe, resource-limited subprocess, planter STEP/STL/GLB generation, and typed browser GLB import; dependency remains optional
- [x] M9 — mock, local-folder, and disabled TRELLIS provider interfaces documented
- [x] M10 — responsive UI, reduced-motion preference, diagnostics, JSON/PNG exports, browser QA
- [x] M11 — project-scoped configurable crews, weighted consensus, advisory/approval/auto-build modes, and server-gated Responses API adapter
- [x] M12 — denser Manhattan skyline, building windows/rooftops, crosswalks, streetlights, trees, and moving block-style traffic
- [x] M13 — validated reversible component demolition with protected base systems and stable-ID undo

## 2026-07-23 iteration verification

- `pnpm --filter @skyfoundry/web typecheck` — passed.
- `pnpm --filter @skyfoundry/web test` — passed three tests including reversible DSL demolition and protected-system checks.
- `pnpm --filter @skyfoundry/agent-client typecheck && pnpm --filter @skyfoundry/agent-client test` — passed; client now targets Responses API structured output.
- `PYTHONPATH=apps/orchestrator .venv/bin/pytest -q apps/orchestrator/tests/test_api.py` — passed seven tests including custom crew validation, consensus, flat live output schema, and disabled-live-provider gating.
- One capped `gpt-5.4-nano` Responses API smoke call — passed with a schema-valid approval and one server-constructed `add_note` action; the credential was process-only and immediately unset.
- Local live-provider configuration now uses an ignored, mode-`600` root `.env`; `pnpm dev:orchestrator` loads it without placing credentials in browser state or source control.
- `pnpm install --frozen-lockfile` — passed after the security lockfile update.
- `pnpm demo:seed` — passed; 1,764 components, 118 tasks, seven actions.
- `pnpm validate:project` — passed; 1,764 components, seven idempotent actions, sequence seven.
- `pnpm lint`, `pnpm typecheck`, and `pnpm build` — passed on the final source.
- `pnpm test` — passed 16 TypeScript tests and nine Python API/CAD tests; the upstream LangGraph deprecation warning remains.
- `pnpm test:e2e` — passed two Chromium scenarios after rendered crew, demolition, night, mobile, and street-camera inspection; the test checks console/page errors.
- `pnpm audit --prod` — initially found the new transitive sharp/libvips advisory, then passed with no known vulnerabilities after pinning `sharp` 0.35.0.
- Final completed-scene measurement — healthy WebGL context, 50 draw calls, 40,792 triangles, 50 geometries, zero textures, DPR 1, and 28 browser rAF callbacks/s under software-rendered headless Chrome.

## Verification log

- `pnpm install --frozen-lockfile` — passed; all nine workspaces already up to date in 611 ms.
- `pnpm demo:seed` — passed; 1,764 components, 118 tasks, seven DSL actions.
- `pnpm validate:project` — passed; seven idempotent actions and projection sequence seven.
- `pnpm lint` — passed across all TypeScript workspaces and the web ESLint configuration with zero warnings.
- `pnpm typecheck` — passed across eight source workspaces.
- `pnpm test` — passed 15 TypeScript tests and six Python API/CAD tests; one LangGraph dependency deprecation warning remains.
- `pnpm build` — passed; Next.js generated all four static routes and reported a 103 kB shared first load.
- `pnpm test:e2e` — passed two Chromium tests in 31.2 seconds on the final run.
- `pnpm audit --prod` — passed with no known vulnerabilities.
- Optional CAD command — passed; STEP 30,868 B, STL 17,484 B, GLB 7,288 B.
- FastAPI smoke — `/health` and `/api/providers` returned HTTP 200 with scripted active and all optional providers disabled.

## Review log

- Architecture: action log confirmed as canonical; Three.js remains a derived projection.
- Three.js: removed remote HDR and inert Rapier critical-path wrapper after browser evidence showed repeatable context loss; dynamic instance buffers and frame-based readiness added.
- Browser QA: fixed blank canvas, camera occlusion, section mode, night lighting, mobile drawers, reduced-motion rate, export menu, inspector visibility/focus, and replay assertion.
- Security: strict schemas, validation gateways, Python operation union, and production dependency audit passed; no critical residual finding.
- Test: final re-review confirmed the visible 0/7 → validated patches → 7/7 product loop and found no remaining Definition-of-Done blocker.

## Remaining limitations

- Live text/state consensus was exercised once; canonical screenshot bytes are not yet attached to live Responses API calls.
- OSM and TRELLIS remain disabled; TRELLIS was not installed.
- Whole-project GLB export is adapter-ready but the MVP exports project/scene/timeline JSON and PNG. The optional CAD part exports GLB.
- The available headless Chromium uses software rendering; completed-scene measurements were 42 draw calls, 26,852 triangles, 42 geometries, zero textures, no context loss, 0.7 ms explicit render, and 36 browser rAF callbacks/s. Hardware-GPU profiling remains future work.
- The CAD child has strong process/Python limits, but a production deployment should add OS/container network isolation.
