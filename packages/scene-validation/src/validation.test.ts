import {describe,expect,it} from 'vitest';import {emptyProjection} from '@skyfoundry/building-dsl';import {validateActions,validateTaskDag} from './index';
const component={id:'tower/column/1',type:'column' as const,generator:'rectangular_column' as const,parameters:{width:.8,depth:.8,height:4},transform:{position:[0,2,0] as [number,number,number],rotation:[0,0,0] as [number,number,number],scale:[1,1,1] as [number,number,number]},tags:[],metadata:{},createdBy:'structural',roundId:'r1'};
const action=(operation:unknown,estimatedComponentCount=0)=>({id:'a1',schemaVersion:'1.0',roundId:'r1',agentId:'structural',timestamp:'2026-01-01T00:00:00.000Z',operation,rationale:'Test constrained action',goalIds:['g1'],dependsOn:[],confidence:1,estimatedComponentCount});
describe('validation gateway',()=>{
  it('detects task cycles',()=>expect(validateTaskDag([{id:'a',predecessorIds:['b']},{id:'b',predecessorIds:['a']}])).toHaveLength(1));
  it('rejects duplicate IDs within one array',()=>expect(validateActions([action({kind:'add_component_array',idPattern:'tower/{i}',components:[component,component]},2)],emptyProjection()).valid).toBe(false));
  it('rejects updates to missing components',()=>expect(validateActions([action({kind:'update_component',componentId:'missing/id',patch:{tags:['x']}})],emptyProjection()).issues.some(i=>i.code==='missing_target')).toBe(true));
  it('rejects unknown generators and unsafe values at schema boundary',()=>expect(validateActions([action({kind:'add_component',component:{...component,generator:'execute_python',parameters:{url:'file:///etc/passwd'}}},1)],emptyProjection()).valid).toBe(false));
  it('rejects provenance mismatches',()=>expect(validateActions([action({kind:'add_component',component:{...component,createdBy:'attacker'}},1)],emptyProjection()).issues.some(i=>i.code==='provenance')).toBe(true));
});
