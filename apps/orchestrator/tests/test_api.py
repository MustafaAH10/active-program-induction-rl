import os, tempfile
fd, path = tempfile.mkstemp(suffix=".db"); os.close(fd); os.environ["SKYFOUNDRY_DB"] = path
from fastapi.testclient import TestClient
from skyfoundry.main import app

client = TestClient(app)
def test_scripted_flow_without_credentials():
    assert client.get("/health").json()["provider"] == "scripted"
    project = client.post("/api/projects").json(); project_id = project["project_id"]
    brief = {"prompt":"Build a 28-storey tower","location_preset":"manhattan","preferred_floors":28,"podium_floors":3,"style_keywords":["tapered"]}
    assert client.post(f"/api/projects/{project_id}/brief", json=brief).status_code == 200
    result = client.post(f"/api/projects/{project_id}/run").json()
    assert result["status"] == "complete" and len(result["proposals"]) >= 6 and len(result["accepted_action_ids"]) >= 6
    actions = client.get(f"/api/projects/{project_id}/actions").json()["actions"]
    assert len(actions) >= 6 and all(a["operation"]["kind"] == "add_note" for a in actions)
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
