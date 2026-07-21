import{describe,expect,it}from'vitest';import{descriptorFor,estimateAsset,generatorIds}from'./index';
describe('factory',()=>it('supports required generators',()=>{expect(generatorIds).toContain('tower_crane');expect(descriptorFor('slab',{width:2,height:.2,depth:2}).kind).toBe('box');expect(estimateAsset('box',{}).triangles).toBe(12)}));
