import { z } from 'zod';

export type GeometryDescriptor={kind:'box'|'cylinder'|'plane';args:number[]};
export type MaterialPreset={id:string;color:string;metalness:number;roughness:number;opacity?:number;emissive?:string;emissiveIntensity?:number};
export const materials:Record<string,MaterialPreset>={
  concrete:{id:'concrete',color:'#7d8588',metalness:.05,roughness:.78}, polished_concrete:{id:'polished_concrete',color:'#aeb5b4',metalness:.08,roughness:.45},
  dark_steel:{id:'dark_steel',color:'#162028',metalness:.82,roughness:.24}, galvanized_steel:{id:'galvanized_steel',color:'#89979e',metalness:.72,roughness:.3},
  blue_glass:{id:'blue_glass',color:'#4f91a8',metalness:.35,roughness:.15,opacity:.72}, clear_glass:{id:'clear_glass',color:'#a8d5dc',metalness:.15,roughness:.08,opacity:.45},
  stone:{id:'stone',color:'#b7aa95',metalness:.02,roughness:.82}, wood:{id:'wood',color:'#8a5c3e',metalness:0,roughness:.75}, aluminum:{id:'aluminum',color:'#aab6bb',metalness:.88,roughness:.2},
  safety_orange:{id:'safety_orange',color:'#ff7a18',metalness:.2,roughness:.45}, soil:{id:'soil',color:'#49362b',metalness:0,roughness:1}, asphalt:{id:'asphalt',color:'#20262b',metalness:.05,roughness:.92},
  vegetation:{id:'vegetation',color:'#4f7d56',metalness:0,roughness:.9}, emissive_interior:{id:'emissive_interior',color:'#ffc36b',metalness:0,roughness:.45,emissive:'#ff9e3d',emissiveIntensity:1.6}
};

const dimensionSchema=z.object({width:z.number().positive().optional(),depth:z.number().positive().optional(),height:z.number().positive().optional(),length:z.number().positive().optional(),radius:z.number().positive().optional()}).passthrough();
export const generatorIds=['box','cylinder','extruded_polygon','slab','rectangular_column','circular_column','steel_i_beam','rectangular_beam','brace','concrete_core','stair_flight','curtain_wall_panel','mullion_grid','punched_window_wall','stone_arch_bay','canopy','parapet','crown','tower_crane','scaffold_bay','safety_rail','pile','foundation_mat','excavation_volume','worker_capsule','excavator_proxy','truck_proxy','tree_proxy','streetlight_proxy','cad_extruded_profile'] as const;
export function descriptorFor(generator:string,p:Record<string,unknown>):GeometryDescriptor{
  dimensionSchema.parse(p);const n=(key:string,fallback:number)=>typeof p[key]==='number'?p[key] as number:fallback;
  if(['cylinder','circular_column','pile','worker_capsule','tree_proxy','streetlight_proxy'].includes(generator))return{kind:'cylinder',args:[n('radius',.3),n('radius',.3),n('height',1),generator==='worker_capsule'?8:12]};
  return{kind:'box',args:[n('width',n('length',1)),n('height',1),n('depth',.5)]};
}
export function estimateAsset(generator:string,p:Record<string,unknown>){const d=descriptorFor(generator,p);return{triangles:d.kind==='box'?12:48,instances:1,memoryBytes:d.kind==='box'?288:1152}}
