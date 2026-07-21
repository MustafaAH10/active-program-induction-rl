import { z } from 'zod';

export const componentTypes = [
  'lot','excavation','soil_volume','street','sidewalk','curb','fence','gate','temporary_office','material_stack','dumpster','streetlight','tree','planter','bench',
  'pile','pile_cap','footing','foundation_mat','basement_wall','retaining_wall','grade_beam','core','core_segment','column','mega_column','beam','transfer_beam','brace','outrigger','belt_truss','slab','slab_opening','stair','ramp',
  'exterior_wall','curtain_wall_system','curtain_wall_panel','mullion','spandrel','window','door','canopy','louver','parapet','crown','roof_screen','partition','elevator_shaft','elevator_car','mechanical_zone','riser','ceiling','light_fixture',
  'tower_crane','mobile_crane','hoist','scaffold','safety_rail','excavator','concrete_truck','flatbed_truck','forklift','worker','load'
] as const;
export const ComponentTypeSchema = z.enum(componentTypes);
export type ComponentType = z.infer<typeof ComponentTypeSchema>;

export const generatorIds=['box','cylinder','extruded_polygon','slab','rectangular_column','circular_column','steel_i_beam','rectangular_beam','brace','concrete_core','stair_flight','curtain_wall_panel','mullion_grid','punched_window_wall','stone_arch_bay','canopy','parapet','crown','tower_crane','scaffold_bay','safety_rail','pile','foundation_mat','excavation_volume','worker_capsule','excavator_proxy','truck_proxy','tree_proxy','streetlight_proxy','cad_extruded_profile'] as const;
export const GeneratorIdSchema=z.enum(generatorIds);
export const materialIds=['concrete','polished_concrete','dark_steel','galvanized_steel','blue_glass','clear_glass','stone','wood','aluminum','safety_orange','soil','asphalt','vegetation','emissive_interior'] as const;
export const MaterialIdSchema=z.enum(materialIds);
const SafeStringSchema=z.string().max(500).refine(value=>!/(?:https?:\/\/|file:\/\/|\.\.\/|<script|\beval\s*\(|\bfunction\s*\()/i.test(value),'Executable code, URLs, and host paths are not allowed');
export const SafeValueSchema:z.ZodType<unknown>=z.lazy(()=>z.union([SafeStringSchema,z.number().finite().min(-100_000).max(100_000),z.boolean(),z.null(),z.array(SafeValueSchema).max(100),z.record(z.string().max(60),SafeValueSchema).superRefine((value,ctx)=>{if(Object.keys(value).length>60)ctx.addIssue({code:z.ZodIssueCode.custom,message:'Object has too many fields'})})]));
export const SafeRecordSchema=z.record(z.string().max(60),SafeValueSchema).superRefine((value,ctx)=>{if(Object.keys(value).length>60)ctx.addIssue({code:z.ZodIssueCode.custom,message:'Object has too many fields'})});

export const TransformSchema = z.object({
  position: z.tuple([z.number(), z.number(), z.number()]),
  rotation: z.tuple([z.number(), z.number(), z.number()]),
  scale: z.tuple([z.number().positive().max(20), z.number().positive().max(20), z.number().positive().max(20)])
}).strict();
export type Transform = z.infer<typeof TransformSchema>;

export const ComponentSchema = z.object({
  id: z.string().min(1).max(160).regex(/^[a-z0-9/_-]+$/),
  type: ComponentTypeSchema,
  parentId: z.string().max(160).optional(),
  levelId: z.string().max(80).optional(),
  generator: GeneratorIdSchema,
  parameters: SafeRecordSchema,
  transform: TransformSchema,
  materialId: MaterialIdSchema.optional(),
  tags: z.array(z.string().max(40)).max(30),
  metadata: SafeRecordSchema,
  createdBy: z.string().max(80),
  roundId: z.string().max(80),
  taskId: z.string().max(120).optional()
}).strict();
export type Component = z.infer<typeof ComponentSchema>;

export const LevelSchema = z.object({
  id: z.string(), index: z.number().int(), name: z.string(), elevation: z.number(),
  floorToFloorHeight: z.number().positive(),
  use: z.enum(['lobby','retail','office','residential','mechanical','amenity','roof'])
}).strict();
export type Level = z.infer<typeof LevelSchema>;

export const ConstructionPhaseSchema = z.enum(['site_setup','excavation','foundation','core','primary_structure','floor_slabs','facade','roof_crown','public_realm','completion']);
export type ConstructionPhase = z.infer<typeof ConstructionPhaseSchema>;

export const ConstructionTaskSchema = z.object({
  id: z.string(), name: z.string(), phase: ConstructionPhaseSchema,
  componentIds: z.array(z.string()), predecessorIds: z.array(z.string()),
  startTick: z.number().nonnegative(), durationTicks: z.number().positive(), crewType: z.string().optional(),
  equipmentIds: z.array(z.string()),
  animationPreset: z.enum(['fade_and_scale','lift_and_place','crane_pick_and_place','rise_from_ground','concrete_pour','extrude_upward','panel_attach','roll_in_vehicle','worker_walk','excavate','demolish','scaffold_assemble','lights_power_on']),
  status: z.enum(['planned','ready','active','complete','blocked'])
}).strict();
export type ConstructionTask = z.infer<typeof ConstructionTaskSchema>;

export const AgentRoundSchema = z.object({
  id: z.string(), agentId: z.string(), agentName: z.string(), role: z.string(), summary: z.string().max(500),
  rationale: z.string().max(800), actionCount: z.number().int().nonnegative(),
  status: z.enum(['queued','working','accepted','rejected']), validation: z.array(z.string()),
  phase: ConstructionPhaseSchema, startTick: z.number(), screenshot: z.string().optional()
}).strict();
export type AgentRound = z.infer<typeof AgentRoundSchema>;

export const BuildingBriefSchema = z.object({
  projectName: z.string().min(1).max(120), locationPreset: z.enum(['manhattan','generic','sandbox']),
  buildingUse: z.array(z.object({ use: z.enum(['retail','office','residential','hotel','cultural','mixed']), share: z.number().min(0).max(1) }).strict()).min(1),
  targetFloors: z.object({ min: z.number().int().positive(), preferred: z.number().int().positive(), max: z.number().int().positive() }).strict(),
  targetHeightM: z.object({ min: z.number(), preferred: z.number(), max: z.number() }).strict().optional(),
  podiumFloors: z.number().int().nonnegative(), floorToFloorHeightM: z.number().positive(), styleKeywords: z.array(z.string()).max(20),
  massing: z.object({ type: z.enum(['slab','point_tower','stepped','tapered','twisted_concept']), setbacks: z.boolean() }).strict(),
  structureConcept: z.object({ preferred: z.enum(['core_and_frame','braced_frame','tube_concept']) }).strict(),
  facade: z.object({ primarySystem: z.enum(['curtain_wall','punched_window','mixed']), materials: z.array(z.string()), rhythm: z.enum(['regular','expressive','vertical','horizontal']) }).strict(),
  crown: z.object({ type: z.enum(['flat','tapered','lantern','mechanical_screen','garden']) }).strict(),
  publicRealm: z.array(z.string()), constructionFeatures: z.array(z.string()), assumptions: z.array(z.string()), unresolvedQuestions: z.array(z.string())
}).strict();
export type BuildingBrief = z.infer<typeof BuildingBriefSchema>;

export type ValidationIssue = { code: string; severity: 'info'|'warning'|'error'; message: string; componentId?: string };
export type ProjectScene = {
  schemaVersion: '1.0'; projectId: string; name: string; seed: number; brief: BuildingBrief;
  levels: Level[]; components: Component[]; tasks: ConstructionTask[]; agentRounds: AgentRound[];
};
