import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from worker import CadRecipe, trusted_template

def test_recipe_is_strict_and_neutral():
    recipe=CadRecipe.model_validate_json((ROOT/"planter-recipe.json").read_bytes())
    assert trusted_template(recipe)["raw_code"] is False
    with pytest.raises(ValidationError):
        CadRecipe.model_validate({**recipe.model_dump(),"python":"import os"})

@pytest.mark.skipif(importlib.util.find_spec("cadquery") is None,reason="optional CadQuery dependency is not installed")
def test_isolated_planter_exports_step_stl_and_glb(tmp_path:Path):
    result=subprocess.run([sys.executable,str(ROOT/"runner.py"),str(ROOT/"planter-recipe.json"),"--output",str(tmp_path)],capture_output=True,text=True,timeout=30,check=True)
    report=json.loads(result.stdout)
    assert report["status"]=="ok"
    assert {p.name for p in tmp_path.iterdir()}=={"planter.step","planter.stl","planter.glb"}
    assert all(path.stat().st_size<25_000_000 for path in tmp_path.iterdir())
