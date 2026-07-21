import{describe,expect,it}from'vitest';import{OpenAICompatibleAgentProvider}from'./index';
describe('providers',()=>it('keeps live calls disabled without credentials',async()=>await expect(new OpenAICompatibleAgentProvider({baseUrl:'http://invalid',apiKey:'',model:'x'}).propose('',{},[],{})).rejects.toThrow('disabled')));
