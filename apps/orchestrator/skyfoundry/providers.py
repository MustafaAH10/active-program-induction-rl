from typing import Protocol
from .models import AddNoteOperation, AgentProposal, ProjectState, SceneAction

class MultimodalAgentProvider(Protocol):
    async def propose(self, agent_id: str, state: ProjectState, image_paths: list[str]) -> AgentProposal: ...

SCRIPTED = [
    ("brief", "Interpreted the mixed-use tower brief", "Captured explicit concept assumptions."),
    ("architect", "Established podium, tower and plaza massing", "The compact footprint preserves public realm."),
    ("structural", "Aligned a regular frame around the core", "The conceptual load path is visually legible."),
    ("facade", "Applied a vertical blue-gray curtain wall", "Repeated bays protect the browser budget."),
    ("logistics", "Placed crane, hoist and site choreography", "Equipment remains inside the modeled access zone."),
    ("planner", "Scheduled the ten-phase task DAG", "Absolute ticks enable deterministic seeking."),
    ("critic", "Resolved the tapered garden crown", "The silhouette now finishes cleanly."),
    ("controller", "Validated and accepted the action log", "Schema, IDs, scope and budgets passed."),
]

class ScriptedAgentProvider:
    async def propose(self, agent_id: str, state: ProjectState, image_paths: list[str]) -> AgentProposal:
        index = next((i for i, row in enumerate(SCRIPTED) if row[0] == agent_id), 0)
        row = SCRIPTED[index]
        round_id=f"round-{index + 1:02d}"
        action=SceneAction(id=f"action/{round_id}/{agent_id}",round_id=round_id,agent_id=agent_id,operation=AddNoteOperation(kind="add_note",message=row[1]),rationale=row[2],goal_ids=["manhattan-tower"],depends_on=[],confidence=.99,estimated_component_count=0)
        return AgentProposal(agent_id=agent_id, round_id=round_id, summary=row[1], rationale=row[2], actions=[action], validation=["schema_valid", "permission_valid", "budget_valid", "deterministic"], confidence=0.99)

class ReplayAgentProvider:
    def __init__(self, proposals: list[AgentProposal]): self.proposals, self.cursor = proposals, 0
    async def propose(self, agent_id: str, state: ProjectState, image_paths: list[str]) -> AgentProposal:
        if self.cursor >= len(self.proposals): raise RuntimeError("Replay exhausted")
        result = self.proposals[self.cursor]; self.cursor += 1; return result

class OpenAICompatibleAgentProvider:
    """Optional interface placeholder. Network calls stay disabled unless explicitly configured."""
    def __init__(self, api_key: str | None): self.api_key = api_key
    async def propose(self, agent_id: str, state: ProjectState, image_paths: list[str]) -> AgentProposal:
        if not self.api_key: raise RuntimeError("Live agents are disabled")
        raise NotImplementedError("Configure a deployment-specific OpenAI-compatible transport")
