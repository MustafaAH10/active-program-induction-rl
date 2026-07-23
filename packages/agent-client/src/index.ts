import { z } from 'zod';
import { SceneActionSchema } from '@skyfoundry/building-dsl';

export const AgentProposalSchema=z.object({agentId:z.string().max(80),roundId:z.string().max(80),summary:z.string().max(500),observations:z.array(z.string().max(300)).max(20),goalsAddressed:z.array(z.string()).max(20),actions:z.array(SceneActionSchema).max(12),concerns:z.array(z.object({severity:z.enum(['info','warning','error']),message:z.string().max(500)}).strict()).max(20),requestAnotherView:z.array(z.enum(['overview','north_elevation','south_elevation','east_elevation','west_elevation','top','street_corner','selected_component','section_x','section_z','crane','foundation'])).max(4),confidence:z.number().min(0).max(1),shouldPauseForHuman:z.boolean()}).strict();
export type AgentProposal=z.infer<typeof AgentProposalSchema>;

export interface MultimodalAgentProvider{propose(systemPrompt:string,state:Record<string,unknown>,imagePaths:string[],responseSchema:Record<string,unknown>):Promise<AgentProposal>}
export class ReplayAgentProvider implements MultimodalAgentProvider{constructor(private readonly proposals:AgentProposal[]){}private cursor=0;async propose(){const value=this.proposals[this.cursor++];if(!value)throw new Error('Replay exhausted');return AgentProposalSchema.parse(value)}}
export class OpenAICompatibleAgentProvider implements MultimodalAgentProvider{
  constructor(private readonly config:{baseUrl:string;apiKey:string;model:string;timeoutMs?:number}){}
  private outputText(data:any){
    if(typeof data.output_text==='string')return data.output_text;
    for(const item of data.output??[])if(item.type==='message')for(const content of item.content??[])if(content.type==='output_text'&&typeof content.text==='string')return content.text;
    throw new Error('Provider returned no structured text');
  }
  async propose(systemPrompt:string,state:Record<string,unknown>,imagePaths:string[],responseSchema:Record<string,unknown>){
    if(!this.config.apiKey)throw new Error('Live provider is disabled: no API key configured');
    if(typeof window!=='undefined')throw new Error('Live providers are server-only');
    const endpoint=new URL(this.config.baseUrl);if(endpoint.protocol!=='https:'&&!['localhost','127.0.0.1'].includes(endpoint.hostname))throw new Error('Provider base URL must use HTTPS or localhost');
    const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),this.config.timeoutMs??30_000);
    try{const response=await fetch(`${this.config.baseUrl.replace(/\/$/,'')}/responses`,{method:'POST',headers:{authorization:`Bearer ${this.config.apiKey}`,'content-type':'application/json'},signal:controller.signal,body:JSON.stringify({model:this.config.model,reasoning:{effort:'none'},max_output_tokens:1200,store:false,input:[{role:'system',content:[{type:'input_text',text:systemPrompt}]},{role:'user',content:[{type:'input_text',text:JSON.stringify({state,imagePaths:imagePaths.map(path=>path.split('/').at(-1))})}]}],text:{format:{type:'json_schema',name:'agent_proposal',strict:true,schema:responseSchema}}})});if(!response.ok)throw new Error(`Provider error ${response.status}`);const raw=await response.text();if(raw.length>2_000_000)throw new Error('Provider response exceeds 2 MB');const data=JSON.parse(raw) as any;return AgentProposalSchema.parse(JSON.parse(this.outputText(data)))}finally{clearTimeout(timer)}}
}
