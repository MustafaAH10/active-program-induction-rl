# Optional integrations

## Live multimodal agents

Set `ENABLE_LIVE_AGENTS=true`, `AGENT_PROVIDER=openai`, and `OPENAI_API_KEY` only in the orchestrator deployment environment. Choose `gpt-5.4-nano` for the lowest-cost specialist reviews or `gpt-5.6-luna` for a stronger cost-sensitive model. `LIVE_AGENT_MAX_CALLS` applies a deployment cap in addition to each project’s cap.

The adapter uses the Responses API with `store: false`, `reasoning.effort: none`, a 1,200-token output ceiling, and a flat strict JSON schema. The model returns review text and a vote; trusted server code creates the allowlisted Building DSL note action. This avoids unsupported schema unions and prevents the model from authoring arbitrary operation shapes.

The scripted provider stays the reference behavior and replay source. Current live calls receive compact structured state and canonical-view names; uploading actual image bytes is intentionally still pending. Keys must never be accepted into browser state, committed to `.env`, or persisted with a project.

## CAD

The base repository validates a bounded `extruded_profile` recipe and translates it to a trusted neutral descriptor. The optional local dependencies were exercised against the planter fixture: the resource-limited subprocess exports STEP/STL/GLB and the browser loads the checked-in GLB through a typed fixture component. Regenerate it with the commands in `apps/cad-worker/README.md`. A production service should add kernel/container network isolation on top of the current socket denial and process limits. Raw generated Python stays disabled.

## TRELLIS-compatible assets

TRELLIS is a separate GPU-heavy service and is never installed automatically. Only decorative categories may use it. Any returned mesh must pass file-type, size, script, triangle-count, and license checks before browser ingestion.
