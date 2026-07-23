from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_max_length=500)

class BuildingBrief(StrictModel):
    project_name: str = "Manhattan Tower Demo"
    prompt: str
    location_preset: Literal["manhattan", "sandbox"] = "manhattan"
    preferred_floors: int = Field(default=28, ge=8, le=80)
    podium_floors: int = Field(default=3, ge=0, le=12)
    style_keywords: list[str] = Field(default_factory=lambda: ["tapered", "warm", "vertical"], max_length=20)

class AddNoteOperation(StrictModel):
    kind: Literal["add_note"]
    message: str = Field(max_length=500)

class SetPhaseOperation(StrictModel):
    kind: Literal["set_phase"]
    phase: Literal["site_setup", "excavation", "foundation", "core", "primary_structure", "floor_slabs", "facade", "roof_crown", "public_realm", "completion"]

SceneOperation = AddNoteOperation | SetPhaseOperation

class SceneAction(StrictModel):
    id: str = Field(pattern=r"^[a-z0-9/_-]+$", max_length=160)
    schema_version: Literal["1.0"] = "1.0"
    round_id: str
    agent_id: str
    operation: SceneOperation = Field(discriminator="kind")
    rationale: str
    goal_ids: list[str] = Field(max_length=20)
    depends_on: list[str] = Field(max_length=50)
    confidence: float = Field(ge=0, le=1)
    estimated_component_count: int = Field(default=0, ge=0, le=2_000)

class AgentProposal(StrictModel):
    agent_id: str
    round_id: str
    summary: str
    rationale: str
    actions: list[SceneAction] = Field(max_length=12)
    validation: list[str] = Field(max_length=20)
    confidence: float = Field(ge=0, le=1)
    vote: Literal["approve", "revise", "block"] = "approve"

class LiveAgentOutput(StrictModel):
    agent_id: str
    round_id: str
    summary: str
    rationale: str
    note: str
    validation: list[str] = Field(max_length=8)
    confidence: float = Field(ge=0, le=1)
    vote: Literal["approve", "revise", "block"]

class AgentDefinition(StrictModel):
    id: str = Field(pattern=r"^[a-z0-9_-]+$", min_length=2, max_length=40)
    name: str = Field(min_length=2, max_length=80)
    role: str = Field(min_length=2, max_length=120)
    specialty: str = Field(min_length=2, max_length=240)
    stance: Literal["creative", "feasibility", "delivery", "critic"] = "creative"
    weight: int = Field(default=1, ge=1, le=3)
    enabled: bool = True

def default_agent_team() -> list[AgentDefinition]:
    return [
        AgentDefinition(id="architect", name="Mara", role="Lead Designer", specialty="Massing, public realm, and a coherent skyline idea", stance="creative", weight=2),
        AgentDefinition(id="civil", name="Eli", role="Civil Concept Reviewer", specialty="Geometric plausibility, site interfaces, and explicit uncertainty", stance="feasibility", weight=2),
        AgentDefinition(id="builder", name="Northstar", role="Construction Company", specialty="Visual sequencing, access, equipment, and delivery clarity", stance="delivery", weight=1),
        AgentDefinition(id="critic", name="Iris", role="City & Visual Critic", specialty="Street experience, silhouette, façade rhythm, and brief alignment", stance="critic", weight=1),
    ]

class AgentTeamConfig(StrictModel):
    mode: Literal["scripted", "live"] = "scripted"
    autonomy: Literal["advisory", "consensus", "auto_build"] = "consensus"
    consensus_threshold: float = Field(default=0.67, ge=0.5, le=1)
    max_rounds: int = Field(default=2, ge=1, le=4)
    max_live_calls: int = Field(default=4, ge=1, le=8)
    model: Literal["gpt-5.4-nano", "gpt-5.6-luna"] = "gpt-5.4-nano"
    agents: list[AgentDefinition] = Field(default_factory=default_agent_team, min_length=2, max_length=8)

    @model_validator(mode="after")
    def validate_team(self):
        enabled = [agent for agent in self.agents if agent.enabled]
        if len(enabled) < 2:
            raise ValueError("At least two agents must be enabled")
        if len({agent.id for agent in self.agents}) != len(self.agents):
            raise ValueError("Agent IDs must be unique")
        return self

class ConsensusResult(StrictModel):
    status: Literal["approved", "revision_required", "blocked"] = "revision_required"
    score: float = Field(ge=0, le=1)
    threshold: float = Field(ge=0.5, le=1)
    approvals: list[str] = Field(default_factory=list, max_length=8)
    objections: list[str] = Field(default_factory=list, max_length=8)
    summary: str = Field(max_length=500)

class ProjectState(StrictModel):
    project_id: str
    user_brief: str
    brief: BuildingBrief | None = None
    current_phase: str = "briefing"
    round_index: int = 0
    proposals: list[AgentProposal] = Field(default_factory=list)
    accepted_action_ids: list[str] = Field(default_factory=list)
    agent_config: AgentTeamConfig = Field(default_factory=AgentTeamConfig)
    consensus: ConsensusResult | None = None
    status: Literal["briefing", "concept", "planning", "building", "review", "revision", "complete", "failed"] = "briefing"

class RevisionRequest(StrictModel):
    prompt: str
