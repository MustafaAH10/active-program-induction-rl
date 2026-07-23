from typing import TypedDict
from langgraph.graph import END, START, StateGraph
from .models import AgentDefinition, AgentTeamConfig, ConsensusResult, ProjectState
from .providers import MultimodalAgentProvider, ScriptedAgentProvider

class GraphState(TypedDict):
    project: ProjectState

def make_node(agent: AgentDefinition, provider: MultimodalAgentProvider):
    async def node(state: GraphState) -> GraphState:
        project = state["project"]
        proposal = await provider.propose(agent, project, [])
        accepted = [action for action in proposal.actions if action.agent_id == agent.id and action.round_id == proposal.round_id and action.id not in project.accepted_action_ids]
        if len(accepted) != len(proposal.actions):
            raise ValueError(f"Rejected invalid or duplicate actions from {agent.id}")
        project.proposals.append(proposal)
        project.accepted_action_ids.extend(a.id for a in accepted)
        project.round_index += 1
        project.current_phase = proposal.round_id
        project.status = "building"
        return {"project": project}
    return node

def consensus_node(config: AgentTeamConfig):
    async def node(state: GraphState) -> GraphState:
        project = state["project"]
        weights = {agent.id: agent.weight for agent in config.agents if agent.enabled}
        total = sum(weights.values())
        approved = [proposal.agent_id for proposal in project.proposals if proposal.vote == "approve"]
        objections = [proposal.agent_id for proposal in project.proposals if proposal.vote != "approve"]
        score = sum(weights.get(agent_id, 0) for agent_id in approved) / total if total else 0
        blocked = any(proposal.vote == "block" for proposal in project.proposals)
        status = "blocked" if blocked else "approved" if score >= config.consensus_threshold else "revision_required"
        project.consensus = ConsensusResult(
            status=status, score=round(score, 3), threshold=config.consensus_threshold,
            approvals=approved, objections=objections,
            summary=f"{len(approved)} of {len(project.proposals)} agents approved; weighted consensus {score:.0%}.",
        )
        project.status = "complete" if status == "approved" else "review"
        return {"project": project}
    return node

def build_graph(config: AgentTeamConfig, provider: MultimodalAgentProvider):
    graph = StateGraph(GraphState)
    agents = [agent for agent in config.agents if agent.enabled]
    ids = [agent.id for agent in agents]
    for agent in agents: graph.add_node(agent.id, make_node(agent, provider))
    graph.add_node("consensus", consensus_node(config))
    graph.add_edge(START, ids[0])
    for current, nxt in zip(ids, ids[1:]): graph.add_edge(current, nxt)
    graph.add_edge(ids[-1], "consensus")
    graph.add_edge("consensus", END)
    return graph.compile()

def default_scripted_graph():
    return build_graph(AgentTeamConfig(), ScriptedAgentProvider())
