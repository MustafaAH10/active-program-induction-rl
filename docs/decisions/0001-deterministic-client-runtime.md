# ADR 0001: deterministic client runtime

SkyFoundry treats the versioned Building DSL action log as the only scene write boundary. A deterministic fixture generator produces validated actions, construction tasks, and stable component IDs. React owns interface state; Zustand owns simulation and project state; React Three Fiber renders derived component records without mutating project data. The Python service mirrors the scripted agent graph for optional orchestration and persistence, but the credential-free demo does not depend on it.

