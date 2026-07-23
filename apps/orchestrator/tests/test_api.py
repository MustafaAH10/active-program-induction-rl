import asyncio, os, tempfile
fd, path = tempfile.mkstemp(suffix=".db"); os.close(fd); os.environ["SKYFOUNDRY_DB"] = path
import httpx
from skyfoundry.main import app

class AsyncTestClient:
    def request(self, method: str, path: str, **kwargs):
        async def run():
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                return await client.request(method, path, **kwargs)
        return asyncio.run(run())
    def get(self, path: str, **kwargs): return self.request("GET", path, **kwargs)
    def post(self, path: str, **kwargs): return self.request("POST", path, **kwargs)
    def put(self, path: str, **kwargs): return self.request("PUT", path, **kwargs)

client = AsyncTestClient()
def test_scripted_flow_without_credentials():
    assert client.get("/health").json()["provider"] == "scripted"
    project = client.post("/api/projects").json(); project_id = project["project_id"]
    brief = {"prompt":"Build a 28-storey tower","location_preset":"manhattan","preferred_floors":28,"podium_floors":3,"style_keywords":["tapered"]}
    assert client.post(f"/api/projects/{project_id}/brief", json=brief).status_code == 200
    result = client.post(f"/api/projects/{project_id}/run").json()
    assert result["status"] == "complete" and len(result["proposals"]) >= 4 and len(result["accepted_action_ids"]) >= 4
    assert result["consensus"]["status"] == "approved" and result["consensus"]["score"] == 1
    actions = client.get(f"/api/projects/{project_id}/actions").json()["actions"]
    assert len(actions) >= 4 and all(a["operation"]["kind"] == "add_note" for a in actions)
    revision = client.post(f"/api/projects/{project_id}/revise", json={"prompt":"make the crown more tapered"}).json()
    assert revision["status"] == "preview" and revision["requiresApproval"]

def test_unknown_fields_are_rejected():
    project_id = client.post("/api/projects").json()["project_id"]
    response = client.post(f"/api/projects/{project_id}/brief", json={"prompt":"Tower","unexpected":"unsafe"})
    assert response.status_code == 422

def test_arbitrary_operations_are_rejected():
    from pydantic import ValidationError
    from skyfoundry.models import SceneAction
    try:
        SceneAction.model_validate({"id":"bad/action","round_id":"r1","agent_id":"bad","operation":{"kind":"execute_python","code":"open('/etc/passwd')"},"rationale":"bad","goal_ids":[],"depends_on":[],"confidence":1})
        assert False, "unsafe operation was accepted"
    except ValidationError:
        pass

def test_sse_order_and_missing_project():
    project_id = client.post("/api/projects").json()["project_id"]
    body = client.get(f"/api/projects/{project_id}/events").text
    assert body.index('"type": "agent_started"') < body.index('"type": "round_completed"') < body.index('"type": "run_completed"')
    assert client.get("/api/projects/missing").status_code == 404

def test_project_agent_crew_is_customizable_and_validated():
    project_id = client.post("/api/projects").json()["project_id"]
    config = {
        "mode":"scripted","autonomy":"auto_build","consensus_threshold":0.75,"max_rounds":2,"max_live_calls":3,"model":"gpt-5.4-nano",
        "agents":[
            {"id":"designer","name":"Mara","role":"Designer","specialty":"Massing and public space","stance":"creative","weight":2,"enabled":True},
            {"id":"civil","name":"Eli","role":"Civil reviewer","specialty":"Site geometry and uncertainty","stance":"feasibility","weight":2,"enabled":True},
            {"id":"builder","name":"Northstar","role":"Builder","specialty":"Sequencing and site delivery","stance":"delivery","weight":1,"enabled":True},
        ],
    }
    response = client.put(f"/api/projects/{project_id}/agent-config", json=config)
    assert response.status_code == 200 and response.json()["agent_config"]["autonomy"] == "auto_build"
    invalid = {**config, "agents":[config["agents"][0]]}
    assert client.put(f"/api/projects/{project_id}/agent-config", json=invalid).status_code == 422

def test_live_agents_require_server_side_enablement():
    project_id = client.post("/api/projects").json()["project_id"]
    project = client.get(f"/api/projects/{project_id}").json()
    config = {**project["agent_config"], "mode":"live"}
    assert client.put(f"/api/projects/{project_id}/agent-config", json=config).status_code == 200
    response = client.post(f"/api/projects/{project_id}/run")
    assert response.status_code == 409

def test_live_output_schema_is_flat_for_strict_structured_outputs():
    import json
    from skyfoundry.models import LiveAgentOutput
    schema = LiveAgentOutput.model_json_schema()
    assert "oneOf" not in json.dumps(schema)
    parsed = LiveAgentOutput.model_validate({
        "agent_id":"designer","round_id":"round-01","summary":"Reviewed massing",
        "rationale":"The plaza should stay legible.","note":"Preserve the southwest corner.",
        "validation":["conceptual_only"],"confidence":0.9,"vote":"approve",
    })
    assert parsed.vote == "approve"
