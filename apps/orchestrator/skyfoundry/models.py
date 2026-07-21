from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

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

class ProjectState(StrictModel):
    project_id: str
    user_brief: str
    brief: BuildingBrief | None = None
    current_phase: str = "briefing"
    round_index: int = 0
    proposals: list[AgentProposal] = Field(default_factory=list)
    accepted_action_ids: list[str] = Field(default_factory=list)
    status: Literal["briefing", "concept", "planning", "building", "review", "revision", "complete", "failed"] = "briefing"

class RevisionRequest(StrictModel):
    prompt: str
