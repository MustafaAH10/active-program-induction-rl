import { describe,expect,it } from 'vitest';
import { applyAction,emptyProjection } from './index';
const component={id:'tower/column/1',type:'column' as const,generator:'rectangular_column',parameters:{width:.8,depth:.8,height:4},transform:{position:[0,2,0] as [number,number,number],rotation:[0,0,0] as [number,number,number],scale:[1,1,1] as [number,number,number]},tags:[],metadata:{},createdBy:'structural',roundId:'r1'};
const action={id:'a1',schemaVersion:'1.0' as const,roundId:'r1',agentId:'structural',timestamp:'2026-01-01T00:00:00.000Z',operation:{kind:'add_component' as const,component},rationale:'Add support',goalIds:['g1'],dependsOn:[],confidence:1,estimatedComponentCount:1};
describe('action reducer',()=>{
  it('is idempotent',()=>{const once=applyAction(emptyProjection(),action);const twice=applyAction(once,action);expect(twice).toBe(once);expect(once.components.size).toBe(1)});
  it('rejects extra fields',()=>expect(()=>applyAction(emptyProjection(),{...action,eval:'bad'})).toThrow());
});
