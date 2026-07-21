# SkyFoundry agent rules

- Read `PLAN.md` and `PROGRESS.md` before work.
- Update `PROGRESS.md` after each milestone.
- The deterministic no-key demo is the highest priority.
- Do not let models write arbitrary runtime code.
- All scene mutations use the Building DSL and all external/model output is schema validated.
- Never claim engineering validity.
- Do not install TRELLIS in the default environment or execute unrestricted CadQuery.
- Run focused tests after each change and full checks before completion.
- Use Playwright against the rendered app, capture milestone screenshots, and fix console errors.
- Preserve stable component IDs and prefer robust procedural systems.
- Record architectural decisions in `docs/decisions/` and document optional capabilities.

