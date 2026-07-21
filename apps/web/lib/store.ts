import { create } from 'zustand';
import { createManhattanDemo } from '@skyfoundry/fixture-projects';
import { deterministicTimestamp, type SceneAction } from '@skyfoundry/building-dsl';
import { validateActions, validatedReplay } from '@skyfoundry/scene-validation';
import type { Component } from '@skyfoundry/scene-schema';

const fixture=createManhattanDemo();
type ViewMode='realistic'|'clay'|'structure'|'construction'|'night'|'xray';
type CameraPreset='overview'|'street'|'crane'|'section_x'|'section_z'|'top'|'selected';
type Revision={status:'idle'|'preview'|'applied';prompt:string;affected:string[];before:string;after:string;error?:string};
type Store={
  started:boolean;prompt:string;components:Component[];actions:SceneAction[];tick:number;playing:boolean;speed:number;selectedId?:string;
  acceptedPatchCount:number;
  mode:ViewMode;camera:CameraPreset;quality:'high'|'balanced';leftOpen:boolean;rightOpen:boolean;systems:Record<string,boolean>;hiddenIds:string[];reducedMotion:boolean;
  revision:Revision;diagnostics:boolean;fps:number;
  start:()=>void;setPrompt:(v:string)=>void;setTick:(v:number)=>void;setPlaying:(v:boolean)=>void;setSpeed:(v:number)=>void;select:(id?:string)=>void;
  setMode:(v:ViewMode)=>void;setCamera:(v:CameraPreset)=>void;toggleSystem:(v:string)=>void;toggleComponent:(id:string)=>void;setPanel:(p:'left'|'right',v:boolean)=>void;setReducedMotion:(v:boolean)=>void;
  previewRevision:(prompt:string)=>void;approveRevision:()=>void;undoRevision:()=>void;replay:()=>void;setDiagnostics:(v:boolean)=>void;setFps:(v:number)=>void;
  applyNextScriptedAction:()=>void;
};
export const useStudio=create<Store>((set,get)=>({
  started:false,prompt:'Build a 28-storey mixed-use glass tower on this empty Manhattan lot. Use a stone podium, a tapered crown, warm interior lighting, a public plaza, and a rooftop garden.',
  components:fixture.scene.components,actions:fixture.actions,acceptedPatchCount:0,tick:0,playing:false,speed:4,mode:'realistic',camera:'overview',quality:'high',leftOpen:true,rightOpen:true,hiddenIds:[],
  systems:{context:true,foundation:true,core:true,structure:true,slabs:true,facade:true,equipment:true,workers:true,landscape:true},reducedMotion:false,revision:{status:'idle',prompt:'',affected:[],before:'',after:''},diagnostics:false,fps:60,
  start:()=>set({started:true,playing:true,tick:0,components:[],actions:[],acceptedPatchCount:0,...(typeof window!=='undefined'&&window.innerWidth<800?{leftOpen:false,rightOpen:false}:{})}),setPrompt:prompt=>set({prompt}),setTick:tick=>set({tick:Math.max(0,Math.min(1000,tick)),playing:false}),setPlaying:playing=>set({playing}),setSpeed:speed=>set({speed}),select:selectedId=>set({selectedId,rightOpen:typeof window!=='undefined'&&window.innerWidth<800?false:true}),setMode:mode=>set({mode}),setCamera:camera=>set({camera}),
  toggleSystem:key=>set(s=>({systems:{...s.systems,[key]:!s.systems[key]}})),toggleComponent:id=>set(s=>({hiddenIds:s.hiddenIds.includes(id)?s.hiddenIds.filter(x=>x!==id):[...s.hiddenIds,id]})),setPanel:(p,v)=>set(p==='left'?{leftOpen:v}:{rightOpen:v}),setReducedMotion:reducedMotion=>set({reducedMotion}),setDiagnostics:diagnostics=>set({diagnostics}),setFps:fps=>set({fps}),
  previewRevision:prompt=>{
    const crown=get().components.filter(c=>c.type==='crown'||c.type==='parapet').map(c=>c.id);
    if(!/crown|taper|roof|garden/i.test(prompt))return set({revision:{status:'preview',prompt,affected:[],before:'No matching scoped system',after:'Try a crown, taper, roof, or garden revision.',error:'Revision is outside the deterministic MVP scope.'}});
    set({revision:{status:'preview',prompt,affected:crown,before:'12 m lantern crown · taper 0.58',after:'16 m stepped lantern · taper 0.38 · stronger warm glow'}})
  },
  approveRevision:()=>{
    const s=get();if(!s.revision.affected.length)return;
    const action:SceneAction={id:'action/revision/crown-01',schemaVersion:'1.0',roundId:'round-revision-01',agentId:'critic',timestamp:deterministicTimestamp(10),operation:{kind:'update_component',componentId:'tower-a/roof/crown/main',patch:{parameters:{height:16,taper:.38},tags:['revised','more-tapered'],materialId:'emissive_interior'}},rationale:'Apply the user-approved scoped crown taper revision.',goalIds:['revision-crown'],dependsOn:['action/finish/realm'],confidence:.99,estimatedComponentCount:0};
    const projection=validatedReplay(s.actions);const result=validateActions([action],projection);if(!result.valid)return set({revision:{...s.revision,error:result.issues[0]?.message??'Validation failed'}});
    const actions=[...s.actions,action],next=validatedReplay(actions);set({actions,components:[...next.components.values()],revision:{...s.revision,status:'applied'},tick:790,playing:true})
  },
  undoRevision:()=>{const actions=get().actions.filter(a=>a.id!=='action/revision/crown-01'),next=validatedReplay(actions);set({actions,components:[...next.components.values()],revision:{status:'idle',prompt:'',affected:[],before:'',after:''}})},
  replay:()=>set({tick:0,playing:true,selectedId:undefined,camera:'overview'}),
  applyNextScriptedAction:()=>{const s=get(),nextAction=fixture.actions[s.acceptedPatchCount];if(!nextAction)return;const projection=validatedReplay(s.actions),result=validateActions([nextAction],projection);if(!result.valid)return set({playing:false});const actions=[...s.actions,nextAction],next=validatedReplay(actions);set({actions,components:[...next.components.values()],acceptedPatchCount:s.acceptedPatchCount+1})}
}));
export const demo=fixture.scene;
