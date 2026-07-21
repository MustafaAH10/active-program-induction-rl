import type { ConstructionTask, ConstructionPhase } from '@skyfoundry/scene-schema';

export const phases:ConstructionPhase[]=['site_setup','excavation','foundation','core','primary_structure','floor_slabs','facade','roof_crown','public_realm','completion'];
export const phaseLabels:Record<ConstructionPhase,string>={site_setup:'Site setup',excavation:'Excavation',foundation:'Foundation',core:'Core',primary_structure:'Primary structure',floor_slabs:'Floor slabs',facade:'Façade',roof_crown:'Roof & crown',public_realm:'Public realm',completion:'Completion'};
export const TOTAL_TICKS=1000;

export function taskProgress(task:ConstructionTask,tick:number){return Math.max(0,Math.min(1,(tick-task.startTick)/task.durationTicks))}
export function taskStatus(task:ConstructionTask,tick:number):ConstructionTask['status']{
  const p=taskProgress(task,tick);if(p>=1)return'complete';if(p>0)return'active';return task.predecessorIds.length?'planned':'ready';
}
export function phaseAtTick(tasks:ConstructionTask[],tick:number):ConstructionPhase{
  const active=tasks.filter(t=>tick>=t.startTick).sort((a,b)=>b.startTick-a.startTick)[0];return active?.phase??'site_setup';
}
export function phaseMarkers(tasks:ConstructionTask[]){return phases.map(phase=>({phase,tick:Math.min(...tasks.filter(t=>t.phase===phase).map(t=>t.startTick))})).filter(x=>Number.isFinite(x.tick))}
export function assertDag(tasks:ConstructionTask[]){
  const seen=new Set<string>(),stack=new Set<string>(),map=new Map(tasks.map(t=>[t.id,t]));
  const walk=(id:string)=>{if(stack.has(id))throw new Error(`Construction task cycle: ${id}`);if(seen.has(id))return;stack.add(id);for(const p of map.get(id)?.predecessorIds??[])walk(p);stack.delete(id);seen.add(id)};tasks.forEach(t=>walk(t.id));return true;
}

