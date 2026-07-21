import type { AgentRound, BuildingBrief, Component, ConstructionPhase, ConstructionTask, Level, ProjectScene } from '@skyfoundry/scene-schema';
import { deterministicTimestamp, type SceneAction } from '@skyfoundry/building-dsl';
import { validatedReplay } from '@skyfoundry/scene-validation';

const T=(position:[number,number,number],scale:[number,number,number]=[1,1,1],rotation:[number,number,number]=[0,0,0])=>({position,rotation,scale});
const comp=(partial:Omit<Component,'transform'|'parameters'|'tags'|'metadata'> & {transform?:Component['transform'];parameters?:Record<string,unknown>;tags?:string[];metadata?:Record<string,unknown>}):Component=>({transform:T([0,0,0]),parameters:{},tags:[],metadata:{},...partial});

export const defaultBrief:BuildingBrief={
  projectName:'Manhattan Tower Demo',locationPreset:'manhattan',buildingUse:[{use:'retail',share:.1},{use:'office',share:.9}],
  targetFloors:{min:24,preferred:28,max:32},targetHeightM:{min:95,preferred:112,max:130},podiumFloors:3,floorToFloorHeightM:3.8,
  styleKeywords:['quiet luxury','vertical','warm','tapered'],massing:{type:'tapered',setbacks:true},structureConcept:{preferred:'core_and_frame'},
  facade:{primarySystem:'curtain_wall',materials:['blue glass','aluminum','stone'],rhythm:'vertical'},crown:{type:'garden'},
  publicRealm:['public plaza','street trees','benches','planters'],constructionFeatures:['tower crane','external hoist','scaffold','workers'],
  assumptions:['Concept dimensions only','Local stylized context','Fictional construction schedule'],unresolvedQuestions:[]
};

const agentDefs=[
  ['brief','Brief Interpreter','Program synthesis','Interpreted a 28-storey mixed-use brief with editable concept assumptions.','The prompt is specific enough for a deterministic massing study.','site_setup'],
  ['architect','Lead Architect','Massing & design','Established a stone podium, slender tower, setbacks and a rooftop garden.','A compact point tower preserves a generous southwest plaza.','site_setup'],
  ['structural','Structural Concept Agent','Concept frame','Proposed a central concrete core with a regular perimeter frame.','A simple aligned frame creates a visually legible conceptual load path.','foundation'],
  ['facade','Façade Designer','Envelope','Developed a blue-gray curtain wall with warm spandrels and vertical fins.','Repeated bays keep the façade crisp while protecting the render budget.','facade'],
  ['logistics','Site Logistics Agent','Site choreography','Placed the crane, hoist, vehicles, staging and worker routes.','A single east-side crane keeps the plaza and access lane readable.','site_setup'],
  ['planner','Construction Planner','Sequence','Scheduled ten phases with structure advancing ahead of the façade.','Absolute-tick tasks make pause, scrub and replay deterministic.','primary_structure'],
  ['critic','Visual Critic','Review','Resolved the crown silhouette and strengthened the illuminated garden lantern.','The tapered crown gives the skyline a clear, intentional finish.','roof_crown'],
  ['controller','Build Controller','Validation','Accepted schema-valid actions within lot, ID and component budgets.','All mutations passed the deterministic validation gateway.','completion']
] as const;

export const agentRounds:AgentRound[]=agentDefs.map((a,i)=>({id:`round-${String(i+1).padStart(2,'0')}`,agentId:a[0],agentName:a[1],role:a[2],summary:a[3],rationale:a[4],actionCount:i===0?1:i===7?0:1,status:'accepted',validation:i===7?['1,764 logical components','No duplicate IDs','Task graph acyclic']:['Schema valid','Within project bounds','Budget accepted'],phase:a[5] as ConstructionPhase,startTick:i*115,screenshot:i===6?'overview':undefined}));

function levels():Level[]{return Array.from({length:29},(_,i)=>({id:i===28?'level-roof':`level-${String(i+1).padStart(2,'0')}`,index:i,name:i===28?'Roof':`Level ${i+1}`,elevation:i*3.8,floorToFloorHeight:3.8,use:i===0?'lobby':i<3?'retail':i===27?'amenity':i===28?'roof':'office'}))}

function task(id:string,name:string,phase:ConstructionPhase,componentIds:string[],startTick:number,durationTicks:number,predecessorIds:string[]=[],animationPreset:ConstructionTask['animationPreset']='fade_and_scale'):ConstructionTask{return{id,name,phase,componentIds,predecessorIds,startTick,durationTicks,equipmentIds:phase==='primary_structure'||phase==='facade'?['site/crane/tower-01']:[],animationPreset,status:'planned'}}

function buildTasks():ConstructionTask[]{
  const tasks:ConstructionTask[]=[
    task('task/site','Mobilize site','site_setup',[],0,55,[],'roll_in_vehicle'),task('task/excavate','Excavate lot','excavation',['site/excavation/main'],55,60,['task/site'],'excavate'),
    task('task/foundation','Install piles and mat','foundation',[],115,60,['task/excavate'],'concrete_pour')
  ];
  for(let f=0;f<28;f++){
    const n=String(f+1).padStart(2,'0'); const prior=f?`task/core/${String(f).padStart(2,'0')}`:'task/foundation';
    tasks.push(task(`task/core/${n}`,`Core — level ${f+1}`,'core',[`tower-a/level/${n}/core/main`],175+f*10,18,[prior],'extrude_upward'));
    tasks.push(task(`task/frame/${n}`,`Frame — level ${f+1}`,'primary_structure',[],195+f*11,20,[`task/core/${n}`],'crane_pick_and_place'));
    tasks.push(task(`task/slab/${n}`,`Slab — level ${f+1}`,'floor_slabs',[`tower-a/level/${n}/slab/main`],207+f*11,14,[`task/frame/${n}`],'concrete_pour'));
    tasks.push(task(`task/facade/${n}`,`Façade — level ${f+1}`,'facade',[],315+f*15,24,[`task/slab/${n}`],'panel_attach'));
  }
  tasks.push(task('task/crown','Assemble crown and roof garden','roof_crown',[],805,75,['task/core/28'],'rise_from_ground'));
  tasks.push(task('task/realm','Complete plaza and landscape','public_realm',[],875,65,['task/facade/28'],'fade_and_scale'));
  tasks.push(task('task/complete','Commission concept lighting','completion',[],940,60,['task/crown','task/realm'],'lights_power_on'));
  return tasks;
}

function siteComponents():Component[]{
  const out:Component[]=[
    comp({id:'site/lot/main',type:'lot',generator:'box',parameters:{width:52,height:.12,depth:42},transform:T([0,.06,0]),materialId:'concrete',createdBy:'architect',roundId:'round-02'}),
    comp({id:'site/excavation/main',type:'excavation',generator:'excavation_volume',parameters:{width:42,height:7,depth:32},transform:T([0,-3.5,0]),materialId:'soil',createdBy:'logistics',roundId:'round-05',taskId:'task/excavate'}),
    comp({id:'site/crane/tower-01',type:'tower_crane',generator:'tower_crane',parameters:{height:126,width:2,depth:2},transform:T([25,63,12]),materialId:'safety_orange',createdBy:'logistics',roundId:'round-05',taskId:'task/site'}),
    comp({id:'site/equipment/excavator-01',type:'excavator',generator:'excavator_proxy',parameters:{width:3,height:2.4,depth:5},transform:T([-15,1.2,13]),materialId:'safety_orange',createdBy:'logistics',roundId:'round-05',taskId:'task/excavate'}),
    comp({id:'site/vehicle/truck-01',type:'concrete_truck',generator:'truck_proxy',parameters:{width:2.5,height:3,depth:6},transform:T([20,1.5,-14]),materialId:'concrete',createdBy:'logistics',roundId:'round-05',taskId:'task/foundation'}),
    comp({id:'site/hoist/east-01',type:'hoist',generator:'box',parameters:{width:2.4,height:110,depth:2.4},transform:T([16,55,0]),materialId:'safety_orange',createdBy:'logistics',roundId:'round-05',taskId:'task/frame/05'})
  ];
  for(let i=0;i<18;i++)out.push(comp({id:`site/worker/${String(i+1).padStart(2,'0')}`,type:'worker',generator:'worker_capsule',parameters:{radius:.22,height:1.7},transform:T([-18+(i%6)*3,.85,12+Math.floor(i/6)*2]),materialId:i%3?'safety_orange':'galvanized_steel',createdBy:'logistics',roundId:'round-05',taskId:'task/site',metadata:{path:'site-loop'}}));
  for(let i=0;i<16;i++){const side=i<8?-1:1;out.push(comp({id:`site/fence/${String(i).padStart(2,'0')}`,type:'fence',generator:'safety_rail',parameters:{width:6,height:2,depth:.08},transform:T([(i%8-3.5)*6,1,side*21]),materialId:'galvanized_steel',createdBy:'logistics',roundId:'round-05',taskId:'task/site'}))}
  for(let i=0;i<12;i++)out.push(comp({id:`site/scaffold/east/${String(i+1).padStart(2,'0')}`,type:'scaffold',generator:'scaffold_bay',parameters:{width:3,height:3.8,depth:1.2},transform:T([16.5,1.9+i*3.8,-9]),materialId:'galvanized_steel',createdBy:'logistics',roundId:'round-05',taskId:`task/facade/${String(Math.min(28,i+5)).padStart(2,'0')}`,metadata:{temporary:true,removeAfterTick:840}}));
  for(let i=0;i<6;i++)out.push(comp({id:`site/material/stack/${String(i+1).padStart(2,'0')}`,type:'material_stack',generator:'box',parameters:{width:2.4,height:.8,depth:1.2},transform:T([-20+i*3.2,.4,-15]),materialId:i%2?'dark_steel':'wood',createdBy:'logistics',roundId:'round-05',taskId:'task/site'}));
  return out;
}

function foundationComponents():Component[]{const out:Component[]=[];for(let x=-15;x<=15;x+=6)for(let z=-10;z<=10;z+=5)out.push(comp({id:`tower-a/foundation/pile/${x+15}-${z+10}`,type:'pile',generator:'pile',parameters:{radius:.38,height:8},transform:T([x,-4,z]),materialId:'concrete',createdBy:'structural',roundId:'round-03',taskId:'task/foundation'}));out.push(comp({id:'tower-a/foundation/mat/main',type:'foundation_mat',generator:'foundation_mat',parameters:{width:38,height:1.5,depth:28},transform:T([0,-.75,0]),materialId:'concrete',createdBy:'structural',roundId:'round-03',taskId:'task/foundation'}));return out}

function structureComponents(){
  const structure:Component[]=[],slabs:Component[]=[],facade:Component[]=[];
  const perimeter:[number,number][]=[[-13,-9],[-4.3,-9],[4.3,-9],[13,-9],[13,9],[4.3,9],[-4.3,9],[-13,9]];
  for(let f=0;f<28;f++){
    const n=String(f+1).padStart(2,'0'),y=f*3.8+1.9,taper=f<22?1:1-(f-21)*.035,w=30*taper,d=22*taper;
    structure.push(comp({id:`tower-a/level/${n}/core/main`,type:'core_segment',levelId:`level-${n}`,generator:'concrete_core',parameters:{width:8,height:3.8,depth:6},transform:T([0,y,0]),materialId:'concrete',createdBy:'structural',roundId:'round-03',taskId:`task/core/${n}`}));
    perimeter.forEach(([x,z],i)=>structure.push(comp({id:`tower-a/level/${n}/column/grid-${i+1}`,type:'column',levelId:`level-${n}`,generator:'rectangular_column',parameters:{width:.7,height:3.65,depth:.7},transform:T([x*taper,y,z*taper]),materialId:'dark_steel',createdBy:'structural',roundId:'round-03',taskId:`task/frame/${n}`,metadata:{grid:`P${i+1}`}})));
    perimeter.forEach(([x,z],i)=>{const [nx,nz]=perimeter[(i+1)%perimeter.length]!;const dx=(nx-x)*taper,dz=(nz-z)*taper,len=Math.hypot(dx,dz);structure.push(comp({id:`tower-a/level/${n}/beam/${i+1}`,type:'beam',levelId:`level-${n}`,generator:'rectangular_beam',parameters:{width:len,height:.45,depth:.35},transform:T([((x+nx)/2)*taper,y+1.55,((z+nz)/2)*taper],[1,1,1],[0,Math.atan2(dz,dx)*180/Math.PI,0]),materialId:'dark_steel',createdBy:'structural',roundId:'round-03',taskId:`task/frame/${n}`,metadata:{supports:[`grid-${i+1}`,`grid-${(i+1)%8+1}`]}}))});
    slabs.push(comp({id:`tower-a/level/${n}/slab/main`,type:'slab',levelId:`level-${n}`,generator:'slab',parameters:{width:w,height:.32,depth:d},transform:T([0,f*3.8+.16,0]),materialId:'polished_concrete',createdBy:'structural',roundId:'round-03',taskId:`task/slab/${n}`}));
    const panelW=w/12,panelD=d/8,panelH=3.35;
    for(let i=0;i<12;i++)for(const side of [-1,1])facade.push(comp({id:`tower-a/level/${n}/facade/${side<0?'north':'south'}/panel/${String(i+1).padStart(2,'0')}`,type:'curtain_wall_panel',levelId:`level-${n}`,generator:'curtain_wall_panel',parameters:{width:panelW-.08,height:panelH,depth:.12},transform:T([-w/2+panelW*(i+.5),y,side*d/2]),materialId:f<3?'stone':(i+f)%7===0?'emissive_interior':'blue_glass',createdBy:'facade',roundId:'round-04',taskId:`task/facade/${n}`,metadata:{orientation:side<0?'north':'south'}}));
    for(let i=0;i<8;i++)for(const side of [-1,1])facade.push(comp({id:`tower-a/level/${n}/facade/${side<0?'west':'east'}/panel/${String(i+1).padStart(2,'0')}`,type:'curtain_wall_panel',levelId:`level-${n}`,generator:'curtain_wall_panel',parameters:{width:panelD-.08,height:panelH,depth:.12},transform:T([side*w/2,y,-d/2+panelD*(i+.5)],[1,1,1],[0,90,0]),materialId:f<3?'stone':(i+f+3)%7===0?'emissive_interior':'blue_glass',createdBy:'facade',roundId:'round-04',taskId:`task/facade/${n}`,metadata:{orientation:side<0?'west':'east'}}));
  }
  return{structure,slabs,facade};
}

function finishComponents():Component[]{
  const out:Component[]=[comp({id:'tower-a/roof/crown/main',type:'crown',levelId:'level-roof',generator:'crown',parameters:{width:20,height:12,depth:14,taper:.58},transform:T([0,112,0]),materialId:'emissive_interior',createdBy:'critic',roundId:'round-07',taskId:'task/crown',metadata:{revision:0}}),comp({id:'tower-a/roof/parapet/main',type:'parapet',generator:'parapet',parameters:{width:23,height:1.2,depth:17},transform:T([0,107.2,0]),materialId:'dark_steel',createdBy:'facade',roundId:'round-04',taskId:'task/crown'})];
  out.push(comp({id:'site/plaza/planter/cad-01',type:'planter',generator:'cad_extruded_profile',parameters:{width:1.2,height:.25,depth:.6},transform:T([-14,.12,15]),materialId:'stone',createdBy:'critic',roundId:'round-07',taskId:'task/realm',metadata:{trustedCadRecipe:true}}));
  for(let i=0;i<28;i++){const n=String(i+1).padStart(2,'0');out.push(comp({id:`tower-a/level/${n}/light/interior`,type:'light_fixture',levelId:`level-${n}`,generator:'box',parameters:{width:18,height:.08,depth:12},transform:T([0,i*3.8+2.7,0]),materialId:'emissive_interior',createdBy:'facade',roundId:'round-04',taskId:'task/complete',metadata:{nightLighting:true}}))}
  for(let i=0;i<12;i++)out.push(comp({id:`site/plaza/tree/${String(i+1).padStart(2,'0')}`,type:'tree',generator:'tree_proxy',parameters:{radius:.7,height:5+(i%3)},transform:T([-21+(i%4)*7,2.5,14+Math.floor(i/4)*5]),materialId:'vegetation',createdBy:'architect',roundId:'round-02',taskId:'task/realm'}));
  for(let i=0;i<8;i++)out.push(comp({id:`site/plaza/bench/${String(i+1).padStart(2,'0')}`,type:'bench',generator:'box',parameters:{width:2.2,height:.45,depth:.65},transform:T([-20+(i%4)*8,.45,12+Math.floor(i/4)*9]),materialId:'wood',createdBy:'architect',roundId:'round-02',taskId:'task/realm'}));
  return out;
}

function action(id:string,roundId:string,agentId:string,operation:SceneAction['operation'],count:number,rationale:string):SceneAction{
  const safeOperation:SceneAction['operation']=operation.kind==='add_component'?{...operation,component:{...operation.component,createdBy:agentId,roundId}}:operation.kind==='add_component_array'?{...operation,components:operation.components.map(component=>({...component,createdBy:agentId,roundId}))}:operation;
  return{id,schemaVersion:'1.0',roundId,agentId,timestamp:deterministicTimestamp(Number(roundId.split('-')[1]??0)),operation:safeOperation,rationale,goalIds:['tower-concept'],dependsOn:[],confidence:.98,estimatedComponentCount:count}
}

export function createManhattanDemo(){
  const lvls=levels(),tasks=buildTasks(),site=siteComponents(),foundation=foundationComponents(),{structure,slabs,facade}=structureComponents(),finish=finishComponents();
  const actions:SceneAction[]=[
    action('action/brief/levels','round-01','brief',{kind:'define_levels',levels:lvls},0,'Define the 28 occupied levels and roof datum.'),
    action('action/site/setup','round-02','architect',{kind:'add_component_array',idPattern:'site/{i}',components:site},site.length,'Establish the lot and construction logistics.'),
    action('action/foundation/system','round-03','structural',{kind:'add_component_array',idPattern:'tower-a/foundation/{i}',components:foundation},foundation.length,'Create a visually plausible pile and mat foundation.'),
    action('action/structure/frame','round-03','structural',{kind:'add_component_array',idPattern:'tower-a/structure/{i}',components:structure},structure.length,'Build the aligned core, columns and perimeter beams.'),
    action('action/structure/slabs','round-06','planner',{kind:'add_component_array',idPattern:'tower-a/slabs/{i}',components:slabs},slabs.length,'Sequence floor plates behind the frame.'),
    action('action/facade/system','round-04','facade',{kind:'add_component_array',idPattern:'tower-a/facade/{i}',components:facade},facade.length,'Attach a repeated high-performance curtain-wall concept.'),
    action('action/finish/realm','round-07','critic',{kind:'add_component_array',idPattern:'tower-a/finish/{i}',components:finish},finish.length,'Resolve the crown and public realm.')
  ];
  const projection=validatedReplay(actions);
  const scene:ProjectScene={schemaVersion:'1.0',projectId:'manhattan-tower',name:'Manhattan Tower Demo',seed:42,brief:defaultBrief,levels:projection.levels,components:[...projection.components.values()],tasks,agentRounds};
  return{scene,actions};
}

export const manhattanContext=[
  {id:'context-1',x:-70,z:-45,w:34,d:28,h:58},{id:'context-2',x:-34,z:-48,w:24,d:25,h:82},{id:'context-3',x:18,z:-50,w:30,d:24,h:52},{id:'context-4',x:58,z:-44,w:32,d:30,h:96},
  {id:'context-5',x:-72,z:45,w:32,d:30,h:74},{id:'context-6',x:-36,z:46,w:24,d:27,h:44},{id:'context-7',x:18,z:48,w:28,d:30,h:68},{id:'context-8',x:58,z:45,w:34,d:28,h:84},
  {id:'context-9',x:-72,z:0,w:28,d:24,h:48},{id:'context-10',x:72,z:0,w:26,d:30,h:62}
];
