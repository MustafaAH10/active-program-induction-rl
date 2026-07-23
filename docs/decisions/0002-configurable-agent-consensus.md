# 0002 — Project-scoped agent crews with server-gated consensus

Status: accepted on 2026-07-23.

## Decision

SkyFoundry stores an `AgentTeamConfig` on each project. A team contains two to eight named specialists with editable roles, specialties, stance, enabled state, and weighted votes. The user chooses advisory, consensus, or auto-build autonomy and a 50–100% approval threshold.

The deterministic scripted provider remains the default. The optional OpenAI provider runs only in the orchestrator when `ENABLE_LIVE_AGENTS=true` and a server environment key is present. Browser state stores team configuration, never credentials. Live calls use the Responses API, strict structured output, `store: false`, bounded output, a maximum-call cap, and the same Pydantic action union used by scripted agents.

`auto_build` does not expand model permissions. It only lets a consensus-approved proposal continue to the existing schema, provenance, scope, dependency, and budget gates. Models can never write runtime code or mutate Three.js directly.

## Cost policy

`gpt-5.4-nano` is the default live model for inexpensive specialist reviews. `gpt-5.6-luna` is an explicit quality/cost step-up. The configuration deliberately excludes expensive flagship models, caps live agents to eight calls, and limits each proposal to 1,200 output tokens.

Current model/API guidance was checked against:

- <https://developers.openai.com/api/docs/models/gpt-5.4-nano>
- <https://developers.openai.com/api/docs/models/gpt-5.6-luna>
- <https://developers.openai.com/api/docs/guides/structured-outputs>
- <https://developers.openai.com/api/docs/guides/migrate-to-responses>

## Consequences

- Crew identity and consensus policy are customizable per user project.
- Deterministic replay and CI remain independent of credentials and API availability.
- Deployment owners control secrets and spending centrally.
- The browser prototype can preview a live-ready crew without falsely implying that a provider is enabled.
- Model output remains conceptual and must not be presented as engineering validity.
