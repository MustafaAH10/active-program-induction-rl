# Architecture

The accepted Building DSL action log is SkyFoundry's canonical scene-write boundary. Fixtures, scripted agents, revisions, replay, imports, and exports all pass through strict Zod or Pydantic contracts. A pure reducer creates a component projection; Three.js is only a rendering cache.

```text
brief → project-scoped agent crew → weighted consensus → strict SceneAction[] → validation
      → idempotent reducer → component registry + task DAG
      → instanced R3F runtime → absolute-tick construction playback
```

## Ownership and dependency direction

- `packages/scene-schema`: domain contracts and budgets.
- `packages/building-dsl`: strict action schema, idempotent reducer, deterministic timestamps.
- `packages/scene-validation`: schema, ID, bounds, parameter, budget, and DAG checks.
- `packages/construction-engine`: pure phase/task/tick calculations.
- `packages/procedural-assets`: allowlisted generators, estimates, and material presets.
- `packages/fixture-projects`: the deterministic Manhattan recipe, action log, tasks, and agent rounds.
- `apps/web`: UI state and a derived Three.js projection. No agent writes Three.js code.
- `apps/orchestrator`: provider-neutral FastAPI/LangGraph/SQLite orchestration and SSE.
- `apps/cad-worker`: optional strict recipe validator and resource-limited subprocess exporter for STEP/STL/GLB.

Zustand owns browser playback, selection, view, and projected component state. Three object references and instance indices are ephemeral and never serialized. Every animation is calculated from the absolute timeline tick, so seek and replay do not depend on prior animation state.

The renderer deliberately avoids remote HDR/map/mesh dependencies. Rapier remains an installed optional integration but is not on the critical render path: its WASM initialization caused repeatable WebGL context loss in the available Chrome/SwiftShader environment, while all required MVP assembly remains deterministic and keyframed.

The bundled CAD planter is an explicitly allowlisted exception to the otherwise procedural runtime. Its typed fixture component points to a local GLB generated from the checked-in recipe. The default install does not require CadQuery; generating it again requires the optional CAD requirements and runs through `runner.py`, never through the browser or agent process.

Each persisted project owns an `AgentTeamConfig`. Crew definitions and consensus thresholds are user data; API credentials are deployment configuration. Scripted and live providers return the same strict Pydantic proposal/action records. Even auto-build consensus cannot bypass the Building DSL validator. Reversible sandbox demolition is represented by validated `remove_component` actions and undo restores the prior action projection while preserving stable component IDs.
