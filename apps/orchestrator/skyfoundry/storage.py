import json, os, sqlite3
from pathlib import Path
from .models import ProjectState

class ProjectStore:
    def __init__(self, path: str | None = None):
        self.path = path or os.getenv("SKYFOUNDRY_DB", "apps/orchestrator/data/skyfoundry.db")
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db: db.execute("CREATE TABLE IF NOT EXISTS projects (id TEXT PRIMARY KEY, state TEXT NOT NULL)")
    def put(self, state: ProjectState):
        with sqlite3.connect(self.path) as db: db.execute("INSERT OR REPLACE INTO projects VALUES (?, ?)", (state.project_id, state.model_dump_json(by_alias=True)))
    def get(self, project_id: str) -> ProjectState | None:
        with sqlite3.connect(self.path) as db: row = db.execute("SELECT state FROM projects WHERE id=?", (project_id,)).fetchone()
        return ProjectState.model_validate_json(row[0]) if row else None

