import {beforeEach,describe,expect,it} from 'vitest';
import {useStudio} from './store';

describe('studio revision gateway',()=>{
  beforeEach(()=>{useStudio.getState().undoRevision();while(useStudio.getState().destroyedActionIds.length)useStudio.getState().restoreLastDestroyed()});
  it('previews and applies a scoped crown revision as a DSL action',()=>{
    useStudio.getState().previewRevision('Make the crown more tapered');
    expect(useStudio.getState().revision.affected).toContain('tower-a/roof/crown/main');
    useStudio.getState().approveRevision();
    expect(useStudio.getState().actions.at(-1)?.operation.kind).toBe('update_component');
    expect(useStudio.getState().components.find(c=>c.id==='tower-a/roof/crown/main')?.parameters.taper).toBe(.38);
  });
  it('routes reversible sandbox demolition through a validated DSL removal',()=>{
    const id=useStudio.getState().components.find(component=>component.type==='curtain_wall_panel')!.id;
    useStudio.getState().select(id);
    useStudio.getState().destroySelected();
    expect(useStudio.getState().actions.at(-1)?.operation).toEqual({kind:'remove_component',componentId:id});
    expect(useStudio.getState().components.some(component=>component.id===id)).toBe(false);
    useStudio.getState().restoreLastDestroyed();
    expect(useStudio.getState().components.some(component=>component.id===id)).toBe(true);
  });
  it('keeps conceptual core and foundation systems protected from sandbox removal',()=>{
    const id=useStudio.getState().components.find(component=>component.type==='core_segment')!.id;
    useStudio.getState().select(id);
    const actionCount=useStudio.getState().actions.length;
    useStudio.getState().destroySelected();
    expect(useStudio.getState().actions).toHaveLength(actionCount);
    expect(useStudio.getState().sandboxMessage).toMatch(/protected base system/i);
  });
});
