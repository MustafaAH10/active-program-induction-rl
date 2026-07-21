import { z } from 'zod';
import { ComponentSchema, LevelSchema, SafeRecordSchema, MaterialIdSchema, type Component, type Level } from '@skyfoundry/scene-schema';

const defineLevels = z.object({ kind:z.literal('define_levels'), levels:z.array(LevelSchema).max(100) }).strict();
const addComponent = z.object({ kind:z.literal('add_component'), component:ComponentSchema }).strict();
const addComponentArray = z.object({
  kind:z.literal('add_component_array'), idPattern:z.string().includes('{i}'), components:z.array(ComponentSchema).max(2000)
}).strict();
const updateComponent = z.object({ kind:z.literal('update_component'), componentId:z.string(), patch:z.object({ parameters:SafeRecordSchema.optional(), materialId:MaterialIdSchema.optional(), tags:z.array(z.string().max(40)).max(30).optional() }).strict() }).strict();
const removeComponent = z.object({ kind:z.literal('remove_component'), componentId:z.string() }).strict();
const note = z.object({ kind:z.enum(['create_project','define_lot','define_grid','attach_component','group_components','add_material','assign_material','add_construction_task','add_animation','add_camera_cue','add_worker_path','add_vehicle_path','set_phase','add_note']), payload:SafeRecordSchema }).strict();

export const SceneOperationSchema = z.union([defineLevels, addComponent, addComponentArray, updateComponent, removeComponent, note]);
export type SceneOperation = z.infer<typeof SceneOperationSchema>;

export const SceneActionSchema = z.object({
  id:z.string().min(1).max(160).regex(/^[a-z0-9/_-]+$/), schemaVersion:z.literal('1.0'), roundId:z.string().max(80), agentId:z.string().max(80),
  timestamp:z.string().datetime(), operation:SceneOperationSchema, rationale:z.string().min(1).max(500), goalIds:z.array(z.string()).max(20),
  dependsOn:z.array(z.string()).max(50), confidence:z.number().min(0).max(1), estimatedComponentCount:z.number().int().min(0).max(2000)
}).strict();
export type SceneAction = z.infer<typeof SceneActionSchema>;

export type SceneProjection = { levels:Level[]; components:Map<string,Component>; appliedActionIds:Set<string>; sequence:number };
export const emptyProjection = ():SceneProjection => ({ levels:[], components:new Map(), appliedActionIds:new Set(), sequence:0 });

export function applyAction(state:SceneProjection, input:unknown):SceneProjection {
  const action=SceneActionSchema.parse(input);
  if(state.appliedActionIds.has(action.id)) return state;
  const next:SceneProjection={ levels:state.levels, components:new Map(state.components), appliedActionIds:new Set(state.appliedActionIds), sequence:state.sequence+1 };
  const op=action.operation;
  if(op.kind==='define_levels') next.levels=op.levels;
  if(op.kind==='add_component') next.components.set(op.component.id,op.component);
  if(op.kind==='add_component_array') for(const component of op.components) next.components.set(component.id,component);
  if(op.kind==='remove_component') next.components.delete(op.componentId);
  if(op.kind==='update_component') {
    const current=next.components.get(op.componentId);
    if(current) next.components.set(op.componentId,{...current,...op.patch,parameters:{...current.parameters,...op.patch.parameters}});
  }
  next.appliedActionIds.add(action.id);
  return next;
}

export function replayActions(actions:unknown[]):SceneProjection { return actions.reduce(applyAction,emptyProjection()); }

export const deterministicTimestamp=(round:number)=>new Date(Date.UTC(2026,0,1,0,round)).toISOString();
