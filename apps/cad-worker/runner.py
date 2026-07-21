"""Isolated launcher for the optional trusted CadQuery child."""
from __future__ import annotations

import argparse
import json
import os
import resource
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from worker import CadRecipe

MAX_OUTPUT_BYTES=25_000_000

def _limits() -> None:
    resource.setrlimit(resource.RLIMIT_CPU,(20,20))
    resource.setrlimit(resource.RLIMIT_AS,(4_000_000_000,4_000_000_000))
    resource.setrlimit(resource.RLIMIT_FSIZE,(MAX_OUTPUT_BYTES,MAX_OUTPUT_BYTES))
    resource.setrlimit(resource.RLIMIT_NOFILE,(64,64))

def run(recipe_path:Path, destination:Path) -> dict:
    payload=recipe_path.read_bytes()
    if len(payload)>65_536:
        raise ValueError("recipe exceeds 64 KiB")
    recipe=CadRecipe.model_validate_json(payload)
    normalized=json.dumps(recipe.model_dump(mode="json"),separators=(",",":"))
    destination=destination.resolve()
    destination.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="skyfoundry-cad-") as raw_job:
        job=Path(raw_job)
        child_recipe=job/"recipe.json"
        child_recipe.write_text(normalized,encoding="utf-8")
        command=[sys.executable,str(Path(__file__).resolve().with_name("worker.py")),"--child","--recipe",str(child_recipe),"--output",str(job)]
        env={"PATH":os.environ.get("PATH","/usr/bin:/bin"),"PYTHONNOUSERSITE":"1","SKYFOUNDRY_CAD_NETWORK":"disabled"}
        result=subprocess.run(command,cwd=job,env=env,stdin=subprocess.DEVNULL,capture_output=True,text=True,timeout=20,check=False,preexec_fn=_limits)
        if result.returncode:
            raise RuntimeError(json.dumps({"status":"error","returncode":result.returncode,"stderr":result.stderr[-2000:]}))
        report=json.loads(result.stdout.strip().splitlines()[-1])
        for entry in report["files"]:
            source=(job/entry["name"]).resolve()
            if job.resolve() not in source.parents or not source.is_file() or source.stat().st_size>MAX_OUTPUT_BYTES:
                raise RuntimeError("child returned an invalid artifact")
            shutil.copyfile(source,destination/source.name)
        return report

def _main() -> None:
    parser=argparse.ArgumentParser(description="Run a constrained SkyFoundry CAD recipe")
    parser.add_argument("recipe",type=Path)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(run(args.recipe,args.output),indent=2))

if __name__=="__main__":
    _main()
