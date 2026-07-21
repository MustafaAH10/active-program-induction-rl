import { SceneActionSchema, applyAction, emptyProjection, type SceneAction, type SceneProjection } from '@skyfoundry/building-dsl';
import type { Component, ValidationIssue } from '@skyfoundry/scene-schema';

export type ValidationResult={valid:boolean;issues:ValidationIssue[];accepted:SceneAction[]};
const limits={components:20_000,instances:50_000,workers:30,vehicles:10};

export function validateActions(inputs:unknown[],projection:SceneProjection):ValidationResult {
  const issues:ValidationIssue[]=[]; const accepted:SceneAction[]=[]; let shadow=projection;
  const roundCounts=new Map<string,number>();for(const input of inputs){const parsed=SceneActionSchema.safeParse(input);if(parsed.success){const key=`${parsed.data.agentId}:${parsed.data.roundId}`,count=(roundCounts.get(key)??0)+1;roundCounts.set(key,count);if(count>12)return{valid:false,issues:[{code:'batch_budget',severity:'error',message:'Agent round exceeds 12 action envelopes'}],accepted:[]}}}
  for(const input of inputs){
    const parsed=SceneActionSchema.safeParse(input);
    if(!parsed.success){issues.push({code:'schema',severity:'error',message:parsed.error.issues[0]?.message??'Invalid action'});continue}
    const action=parsed.data; const op=action.operation;const ids=new Set(shadow.components.keys());const actionIds=new Set(shadow.appliedActionIds);
    const incoming:Component[] = op.kind==='add_component'?[op.component]:op.kind==='add_component_array'?op.components:[];
    if(incoming.length>2000){issues.push({code:'action_budget',severity:'error',message:'Action exceeds 2,000 components'});continue}
    let failed=false;const stagedIds=new Set(ids);
    if(action.dependsOn.some(id=>!actionIds.has(id))){issues.push({code:'missing_action_dependency',severity:'error',message:'Action dependency does not exist'});failed=true}
    if(action.estimatedComponentCount!==incoming.length){issues.push({code:'estimated_count',severity:'error',message:'Estimated component count does not match payload'});failed=true}
    if((op.kind==='update_component'||op.kind==='remove_component')&&!ids.has(op.componentId)){issues.push({code:'missing_target',severity:'error',message:`Target component ${op.componentId} does not exist`,componentId:op.componentId});failed=true}
    for(const c of incoming){
      if(stagedIds.has(c.id)){issues.push({code:'duplicate_id',severity:'error',message:`Duplicate component ID ${c.id}`,componentId:c.id});failed=true;continue}stagedIds.add(c.id);
      if(c.createdBy!==action.agentId||c.roundId!==action.roundId){issues.push({code:'provenance',severity:'error',message:'Component provenance must match its action envelope',componentId:c.id});failed=true}
      const [x,y,z]=c.transform.position;
      if(Math.abs(x)>180||Math.abs(z)>180||y< -15||y>220){issues.push({code:'project_bounds',severity:'error',message:'Component is outside project bounds',componentId:c.id});failed=true}
      const dims=['width','depth','height','length'];
      if(dims.some(k=>typeof c.parameters[k]==='number' && (c.parameters[k] as number)<=0)){issues.push({code:'parameters',severity:'error',message:'Dimensions must be positive',componentId:c.id});failed=true}
      if(dims.some(k=>typeof c.parameters[k]==='number' && (c.parameters[k] as number)>500)){issues.push({code:'parameters',severity:'error',message:'Dimensions exceed the generator envelope',componentId:c.id});failed=true}
    }
    if(incoming.length+shadow.components.size>limits.components){issues.push({code:'project_budget',severity:'error',message:'Logical component budget exceeded'});failed=true}
    if(!failed){accepted.push(action);shadow=applyAction(shadow,action)}
  }
  const workers=[...shadow.components.values()].filter(c=>c.type==='worker').length;
  if(workers>limits.workers)issues.push({code:'worker_budget',severity:'error',message:'Worker budget exceeded'});
  const vehicles=[...shadow.components.values()].filter(c=>['concrete_truck','flatbed_truck','forklift','excavator','mobile_crane'].includes(c.type)).length;
  if(vehicles>limits.vehicles)issues.push({code:'vehicle_budget',severity:'error',message:'Vehicle budget exceeded'});
  return {valid:!issues.some(i=>i.severity==='error'),issues,accepted};
}

export function validatedReplay(inputs:unknown[]):SceneProjection{
  const result=validateActions(inputs,emptyProjection());if(!result.valid||result.accepted.length!==inputs.length)throw new Error(`Action validation failed: ${result.issues.map(i=>`${i.code}: ${i.message}`).join('; ')}`);
  return result.accepted.reduce(applyAction,emptyProjection());
}

export function validateTaskDag(tasks:{id:string;predecessorIds:string[]}[]):ValidationIssue[]{
  const issues:ValidationIssue[]=[];const byId=new Map(tasks.map(t=>[t.id,t]));const visiting=new Set<string>();const done=new Set<string>();
  const visit=(id:string)=>{if(visiting.has(id)){issues.push({code:'task_cycle',severity:'error',message:`Cycle at ${id}`});return}if(done.has(id))return;visiting.add(id);for(const p of byId.get(id)?.predecessorIds??[])if(byId.has(p))visit(p);visiting.delete(id);done.add(id)};
  tasks.forEach(t=>visit(t.id));return issues;
}
