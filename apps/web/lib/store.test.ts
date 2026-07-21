import {beforeEach,describe,expect,it} from 'vitest';
import {useStudio} from './store';

describe('studio revision gateway',()=>{
  beforeEach(()=>useStudio.getState().undoRevision());
  it('previews and applies a scoped crown revision as a DSL action',()=>{
    useStudio.getState().previewRevision('Make the crown more tapered');
    expect(useStudio.getState().revision.affected).toContain('tower-a/roof/crown/main');
    useStudio.getState().approveRevision();
    expect(useStudio.getState().actions.at(-1)?.operation.kind).toBe('update_component');
    expect(useStudio.getState().components.find(c=>c.id==='tower-a/roof/crown/main')?.parameters.taper).toBe(.38);
  });
});
