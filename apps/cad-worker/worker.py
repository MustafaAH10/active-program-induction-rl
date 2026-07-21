"""Trusted CAD-recipe validation and child-process execution.

This module accepts data, never Python source. CadQuery and trimesh are optional
imports that are reached only by the isolated child entry point.
"""
from __future__ import annotations

import argparse
import json
import socket
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

class Profile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["rounded_rectangle", "rectangle", "circle"]
    width: float = Field(gt=0, le=10)
    depth: float = Field(gt=0, le=10)
    radius: float = Field(default=0, ge=0, le=2)

class Hole(BaseModel):
    model_config = ConfigDict(extra="forbid")
    x: float = Field(ge=-5, le=5)
    y: float = Field(ge=-5, le=5)
    diameter: float = Field(gt=0, le=2)

class Fillet(BaseModel):
    model_config = ConfigDict(extra="forbid")
    edgeSelector: Literal["vertical"]
    radius: float = Field(gt=0, le=.25)

class CadRecipe(BaseModel):
    model_config = ConfigDict(extra="forbid")
    primitive: Literal["extruded_profile"]
    units: Literal["m"]
    profile: Profile
    height: float = Field(gt=0, le=10)
    holes: list[Hole] = Field(default_factory=list, max_length=16)
    fillets: list[Fillet] = Field(default_factory=list, max_length=4)

def trusted_template(recipe: CadRecipe) -> dict:
    """Return a bounded neutral solid descriptor; a separately installed worker may translate it to CadQuery."""
    return {
        "operation":"trusted_extrude",
        "profile":recipe.profile.model_dump(),
        "height_m":recipe.height,
        "holes":[hole.model_dump() for hole in recipe.holes],
        "fillets":[fillet.model_dump() for fillet in recipe.fillets],
        "network":False,
        "raw_code":False,
    }

def _deny_network() -> None:
    class DisabledSocket(socket.socket):
        def connect(self, *_args, **_kwargs):
            raise RuntimeError("network access is disabled in the CAD worker")
        def connect_ex(self, *_args, **_kwargs):
            raise RuntimeError("network access is disabled in the CAD worker")
    socket.socket = DisabledSocket

def build_recipe(recipe: CadRecipe, output_dir: Path) -> dict:
    """Build STEP/STL/GLB artifacts using only trusted, bounded operations."""
    _deny_network()
    import cadquery as cq
    import trimesh

    profile = recipe.profile
    if profile.type == "circle":
        solid = cq.Workplane("XY").circle(profile.width / 2).extrude(recipe.height)
    else:
        solid = cq.Workplane("XY").rect(profile.width, profile.depth).extrude(recipe.height)
        edge_radius = profile.radius or (recipe.fillets[0].radius if recipe.fillets else 0)
        if profile.type == "rounded_rectangle" and edge_radius:
            solid = solid.edges("|Z").fillet(min(edge_radius, profile.width / 2.1, profile.depth / 2.1))
    if recipe.holes:
        points = [(hole.x, hole.y) for hole in recipe.holes]
        diameters = {hole.diameter for hole in recipe.holes}
        if len(diameters) != 1:
            raise ValueError("all holes in one bounded recipe must share a diameter")
        solid = solid.faces(">Z").workplane().pushPoints(points).hole(diameters.pop())

    output_dir.mkdir(parents=True, exist_ok=True)
    step_path, stl_path, glb_path = (output_dir / "planter.step", output_dir / "planter.stl", output_dir / "planter.glb")
    cq.exporters.export(solid, str(step_path))
    cq.exporters.export(solid, str(stl_path), tolerance=.002, angularTolerance=.15)
    mesh = trimesh.load_mesh(stl_path, file_type="stl")
    mesh.export(glb_path, file_type="glb")
    files=[]
    for path in (step_path, stl_path, glb_path):
        size=path.stat().st_size
        if size > 25_000_000:
            raise ValueError(f"CAD output exceeds 25 MB cap: {path.name}")
        files.append({"name":path.name,"bytes":size})
    return {"status":"ok","template":trusted_template(recipe),"files":files}

def _main() -> None:
    parser=argparse.ArgumentParser(description="SkyFoundry trusted CAD child")
    parser.add_argument("--child", action="store_true")
    parser.add_argument("--recipe", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args=parser.parse_args()
    if not args.child:
        raise SystemExit("Use runner.py; direct/raw execution is disabled")
    payload=args.recipe.read_bytes()
    if len(payload)>65_536:
        raise ValueError("recipe exceeds 64 KiB")
    recipe=CadRecipe.model_validate_json(payload)
    print(json.dumps(build_recipe(recipe,args.output),separators=(",",":")))

if __name__ == "__main__":
    _main()
