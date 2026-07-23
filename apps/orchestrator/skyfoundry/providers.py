import json
from typing import Protocol
import httpx
from .models import AddNoteOperation, AgentDefinition, AgentProposal, LiveAgentOutput, ProjectState, SceneAction

class MultimodalAgentProvider(Protocol):
    async def propose(self, agent: AgentDefinition, state: ProjectState, image_paths: list[str]) -> AgentProposal: ...

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
    async def propose(self, agent: AgentDefinition, state: ProjectState, image_paths: list[str]) -> AgentProposal:
        agent_id = agent.id
        index = next((i for i, row in enumerate(SCRIPTED) if row[0] == agent_id), 0)
        known = SCRIPTED[index] if any(row[0] == agent_id for row in SCRIPTED) else None
        summary = known[1] if known else f"{agent.name} reviewed the concept from the {agent.role.lower()} perspective"
        rationale = known[2] if known else f"Focused on {agent.specialty.lower()} while keeping all changes inside the validated Building DSL."
        round_id=f"round-{state.round_index + 1:02d}"
        action=SceneAction(id=f"action/{round_id}/{agent_id}",round_id=round_id,agent_id=agent_id,operation=AddNoteOperation(kind="add_note",message=summary),rationale=rationale,goal_ids=["manhattan-tower"],depends_on=[],confidence=.99,estimated_component_count=0)
        return AgentProposal(agent_id=agent_id, round_id=round_id, summary=summary, rationale=rationale, actions=[action], validation=["schema_valid", "permission_valid", "budget_valid", "deterministic"], confidence=0.99, vote="approve")

class ReplayAgentProvider:
    def __init__(self, proposals: list[AgentProposal]): self.proposals, self.cursor = proposals, 0
    async def propose(self, agent: AgentDefinition, state: ProjectState, image_paths: list[str]) -> AgentProposal:
        if self.cursor >= len(self.proposals): raise RuntimeError("Replay exhausted")
        result = self.proposals[self.cursor]; self.cursor += 1; return result

class OpenAICompatibleAgentProvider:
    """Bounded Responses API adapter. It can only return strict proposal records."""
    def __init__(self, api_key: str | None, model: str, base_url: str = "https://api.openai.com/v1", timeout_seconds: float = 30):
        self.api_key, self.model, self.base_url, self.timeout_seconds = api_key, model, base_url.rstrip("/"), timeout_seconds

    @staticmethod
    def _output_text(payload: dict) -> str:
        if isinstance(payload.get("output_text"), str):
            return payload["output_text"]
        for item in payload.get("output", []):
            if item.get("type") == "message":
                for content in item.get("content", []):
                    if content.get("type") == "output_text" and isinstance(content.get("text"), str):
                        return content["text"]
        raise RuntimeError("Live provider returned no structured text")

    async def propose(self, agent: AgentDefinition, state: ProjectState, image_paths: list[str]) -> AgentProposal:
        if not self.api_key: raise RuntimeError("Live agents are disabled")
        round_id = f"round-{state.round_index + 1:02d}"
        schema = LiveAgentOutput.model_json_schema()
        system = (
            "You are a named specialist inside SkyFoundry, a conceptual building simulator. "
            "Never claim architectural, civil, structural, construction, zoning, or safety validity. "
            "Return only the requested strict JSON. You cannot write code or mutate a scene directly. "
            "Your only allowed operations are add_note and set_phase. Keep the rationale concise and purpose-written."
        )
        prompt = {
            "identity": agent.model_dump(),
            "round_id": round_id,
            "brief": state.user_brief,
            "project_status": state.status,
            "recent_proposals": [proposal.model_dump() for proposal in state.proposals[-3:]],
            "instruction": "Review the concept from your role, state one useful proposal, and vote approve, revise, or block. Objections must be conceptual and explicit.",
            "available_views": [path.rsplit("/", 1)[-1] for path in image_paths[:4]],
        }
        body = {
            "model": self.model,
            "reasoning": {"effort": "none"},
            "max_output_tokens": 1200,
            "store": False,
            "input": [
                {"role": "system", "content": [{"type": "input_text", "text": system}]},
                {"role": "user", "content": [{"type": "input_text", "text": json.dumps(prompt)}]},
            ],
            "text": {"format": {"type": "json_schema", "name": "agent_proposal", "strict": True, "schema": schema}},
        }
        headers = {"authorization": f"Bearer {self.api_key}", "content-type": "application/json"}
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(f"{self.base_url}/responses", headers=headers, json=body)
        if response.is_error:
            try:
                detail = str(response.json().get("error", {}).get("message", "request rejected"))
            except ValueError:
                detail = "request rejected"
            raise RuntimeError(f"Live provider error {response.status_code}: {detail[:500]}")
        if len(response.content) > 2_000_000:
            raise RuntimeError("Live provider response exceeds 2 MB")
        output = LiveAgentOutput.model_validate_json(self._output_text(response.json()))
        if output.agent_id != agent.id or output.round_id != round_id:
            raise RuntimeError("Live provider returned mismatched agent provenance")
        action = SceneAction(
            id=f"action/{round_id}/{agent.id}", round_id=round_id, agent_id=agent.id,
            operation=AddNoteOperation(kind="add_note", message=output.note),
            rationale=output.rationale, goal_ids=["manhattan-tower"], depends_on=[],
            confidence=output.confidence, estimated_component_count=0,
        )
        return AgentProposal(
            agent_id=output.agent_id, round_id=output.round_id, summary=output.summary,
            rationale=output.rationale, actions=[action],
            validation=[*output.validation, "server_constructed_dsl"], confidence=output.confidence,
            vote=output.vote,
        )
