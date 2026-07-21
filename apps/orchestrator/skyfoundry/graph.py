from typing import TypedDict
from langgraph.graph import END, START, StateGraph
from .models import ProjectState
from .providers import SCRIPTED, ScriptedAgentProvider

class GraphState(TypedDict):
    project: ProjectState

provider = ScriptedAgentProvider()

def make_node(agent_id: str):
    async def node(state: GraphState) -> GraphState:
        project = state["project"]
        proposal = await provider.propose(agent_id, project, [])
        accepted = [action for action in proposal.actions if action.agent_id == agent_id and action.round_id == proposal.round_id and action.id not in project.accepted_action_ids]
        if len(accepted) != len(proposal.actions):
            raise ValueError(f"Rejected invalid or duplicate actions from {agent_id}")
        project.proposals.append(proposal)
        project.accepted_action_ids.extend(a.id for a in accepted)
        project.round_index += 1
        project.current_phase = proposal.round_id
        project.status = "complete" if agent_id == "controller" else "building"
        return {"project": project}
    return node

def build_graph():
    graph = StateGraph(GraphState)
    ids = [row[0] for row in SCRIPTED]
    for agent_id in ids: graph.add_node(agent_id, make_node(agent_id))
    graph.add_edge(START, ids[0])
    for current, nxt in zip(ids, ids[1:]): graph.add_edge(current, nxt)
    graph.add_edge(ids[-1], END)
    return graph.compile()

scripted_graph = build_graph()
