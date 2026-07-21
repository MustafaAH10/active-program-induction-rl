import {describe,expect,it}from'vitest';import{assertDag,taskProgress}from'./index';
describe('timeline',()=>{it('computes absolute progress',()=>expect(taskProgress({startTick:10,durationTicks:20} as never,20)).toBe(.5));it('rejects cycles',()=>expect(()=>assertDag([{id:'a',predecessorIds:['b']},{id:'b',predecessorIds:['a']}] as never)).toThrow())});

