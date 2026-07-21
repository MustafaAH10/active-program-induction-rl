import { mkdir, writeFile } from 'node:fs/promises';
import { createManhattanDemo } from '../packages/fixture-projects/src/index';
const {scene,actions}=createManhattanDemo();
await mkdir('artifacts/manhattan-tower',{recursive:true});
await writeFile('artifacts/manhattan-tower/project.json',JSON.stringify({...scene,actions},null,2));
await writeFile('artifacts/manhattan-tower/scene.json',JSON.stringify({schemaVersion:scene.schemaVersion,projectId:scene.projectId,components:scene.components},null,2));
await writeFile('artifacts/manhattan-tower/timeline.json',JSON.stringify(scene.tasks,null,2));
console.log(`Seeded ${scene.projectId}: ${scene.components.length} components, ${scene.tasks.length} tasks, ${actions.length} actions.`);
