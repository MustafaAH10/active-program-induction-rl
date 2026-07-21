import { describe, expect, it } from 'vitest';
import { BuildingBriefSchema, ComponentSchema } from './index';

describe('schemas', () => {
  it('rejects unknown component fields and unsafe ids', () => {
    expect(ComponentSchema.safeParse({ id: '../bad', extra: true }).success).toBe(false);
  });
  it('validates a conservative brief', () => {
    expect(BuildingBriefSchema.safeParse({
      projectName:'Tower', locationPreset:'manhattan', buildingUse:[{use:'office',share:1}], targetFloors:{min:24,preferred:28,max:32},
      podiumFloors:3,floorToFloorHeightM:3.8,styleKeywords:['warm'],massing:{type:'tapered',setbacks:true},structureConcept:{preferred:'core_and_frame'},
      facade:{primarySystem:'curtain_wall',materials:['glass'],rhythm:'vertical'},crown:{type:'garden'},publicRealm:[],constructionFeatures:[],assumptions:[],unresolvedQuestions:[]
    }).success).toBe(true);
  });
});
