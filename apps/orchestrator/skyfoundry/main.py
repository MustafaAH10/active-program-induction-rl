import asyncio, json, os
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from .graph import scripted_graph
from .models import BuildingBrief, ProjectState, RevisionRequest
from .providers import SCRIPTED
from .storage import ProjectStore

app = FastAPI(title="SkyFoundry Orchestrator", version="0.1.0")
store = ProjectStore()

@app.get("/health")
def health(): return {"status": "ok", "provider": os.getenv("AGENT_PROVIDER", "scripted")}

@app.get("/api/providers")
def providers(): return {"active": "scripted", "providers": [{"id":"scripted","enabled":True},{"id":"openai_compatible","enabled":False},{"id":"trellis","enabled":False},{"id":"cad","enabled":False}]}

@app.post("/api/projects")
def create_project():
    state = ProjectState(project_id=f"project-{uuid4().hex[:10]}", user_brief="")
    store.put(state); return state

@app.get("/api/projects/{project_id}")
def get_project(project_id: str):
    state = store.get(project_id)
    if not state: raise HTTPException(404, "Project not found")
    return state

@app.post("/api/projects/{project_id}/brief")
def set_brief(project_id: str, brief: BuildingBrief):
    state = store.get(project_id)
    if not state: raise HTTPException(404, "Project not found")
    state.brief, state.user_brief, state.status = brief, brief.prompt, "concept"; store.put(state); return state

@app.post("/api/projects/{project_id}/run")
async def run_project(project_id: str):
    state = store.get(project_id)
    if not state: raise HTTPException(404, "Project not found")
    result = await scripted_graph.ainvoke({"project": state}); store.put(result["project"]); return result["project"]

@app.get("/api/projects/{project_id}/events")
async def stream_events(project_id: str):
    state = store.get(project_id)
    if not state: raise HTTPException(404, "Project not found")
    async def events():
        for index, row in enumerate(SCRIPTED):
            yield f"data: {json.dumps({'type':'agent_started','agentId':row[0],'roundId':f'round-{index+1:02d}'})}\n\n"
            await asyncio.sleep(0.01)
            yield f"data: {json.dumps({'type':'round_completed','roundId':f'round-{index+1:02d}'})}\n\n"
        yield f"data: {json.dumps({'type':'run_completed','projectId':project_id})}\n\n"
    return StreamingResponse(events(), media_type="text/event-stream")

@app.post("/api/projects/{project_id}/revise")
def revise(project_id: str, request: RevisionRequest):
    state = store.get(project_id)
    if not state: raise HTTPException(404, "Project not found")
    scoped = any(word in request.prompt.lower() for word in ("crown", "taper", "roof", "garden"))
    return {"status":"preview" if scoped else "rejected","affectedComponentIds":["tower-a/roof/crown/main"] if scoped else [],"requiresApproval":True,"validation":["schema_valid","scope_valid"] if scoped else ["unsupported_scope"]}

@app.post("/api/projects/{project_id}/pause")
def pause(project_id: str): return {"projectId":project_id,"status":"paused"}
@app.post("/api/projects/{project_id}/resume")
def resume(project_id: str): return {"projectId":project_id,"status":"building"}
@app.get("/api/projects/{project_id}/actions")
def actions(project_id: str):
    state=store.get(project_id)
    if not state: raise HTTPException(404,"Project not found")
    return {"projectId":project_id,"actions":[action for proposal in state.proposals for action in proposal.actions]}
@app.get("/api/projects/{project_id}/tasks")
def tasks(project_id: str): return {"projectId":project_id,"tasks":[{"id":f"task/{index+1:02d}","phase":phase} for index,phase in enumerate(("site_setup","excavation","foundation","core","primary_structure","floor_slabs","facade","roof_crown","public_realm","completion"))]}
@app.get("/api/projects/{project_id}/artifacts")
def artifacts(project_id: str): return {"projectId":project_id,"artifacts":[]}
@app.post("/api/projects/{project_id}/export")
def export(project_id: str): return {"projectId":project_id,"formats":["project_json","scene_json","timeline_json"]}
