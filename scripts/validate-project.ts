import { readFile } from 'node:fs/promises';
import { SceneActionSchema, emptyProjection } from '../packages/building-dsl/src/index';
import { validateActions, validatedReplay } from '../packages/scene-validation/src/index';
const path=process.argv[2];if(!path)throw new Error('Usage: pnpm validate:project <project.json>');
const data=JSON.parse(await readFile(path,'utf8'));if(!Array.isArray(data.actions))throw new Error('Project has no action log');
data.actions.forEach(SceneActionSchema.parse);const validation=validateActions(data.actions,emptyProjection());if(!validation.valid)throw new Error(JSON.stringify(validation.issues));
const projection=validatedReplay(data.actions);if(projection.components.size!==data.components.length)throw new Error('Projection component count does not match snapshot');
console.log(`Valid project: ${projection.components.size} components, ${data.actions.length} idempotent actions, sequence ${projection.sequence}.`);
