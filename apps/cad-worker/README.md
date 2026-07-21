# Safe CAD recipe adapter

The optional CAD worker accepts constrained dimensional recipes only. It does not execute model-generated Python and is disabled by default. CadQuery is intentionally not installed by the base project.

Install and run the optional planter demonstration inside the project virtual environment:

```bash
.venv/bin/pip install -r apps/cad-worker/requirements-optional.txt
.venv/bin/python apps/cad-worker/runner.py apps/cad-worker/planter-recipe.json --output artifacts/cad-planter
```

`runner.py` revalidates the strict Pydantic recipe, normalizes it, and launches a temporary-directory child with a 20-second timeout plus CPU, memory, open-file, output-size, and user-site limits. The child disables socket connections and exposes only a trusted extrusion template. STEP, STL, and GLB are copied out only after path and 25 MB checks. No source-code field exists in the schema; direct worker execution is rejected.
