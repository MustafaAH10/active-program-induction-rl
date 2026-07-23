import { test, expect } from '@playwright/test';
import { mkdir } from 'node:fs/promises';

test.beforeAll(async()=>mkdir('screenshots',{recursive:true}));

test('deterministic Manhattan Tower build, inspection, revision and export', async({page})=>{
  test.setTimeout(90_000);
  const errors:string[]=[];page.on('console',msg=>{if(msg.type()==='error')errors.push(msg.text())});page.on('pageerror',e=>errors.push(e.message));
  await page.goto('/');
  await expect(page.getByRole('heading',{name:/Imagine a tower/i})).toBeVisible();
  await expect(page.getByTestId('accepted-patches')).toContainText('0 / 7');
  await expect(page.getByText(/Conceptual simulation only/).first()).toBeVisible();
  await page.screenshot({path:'screenshots/01-landing.png'});
  await page.getByRole('button',{name:/agent crew/i}).click();
  await expect(page.getByRole('dialog',{name:'Configure agent crew'})).toBeVisible();
  await page.getByLabel('Agent autonomy').selectOption('auto_build');
  await page.getByLabel('architect name').fill('Mara');
  await expect(page.getByText(/API keys stay on the orchestrator server/i)).toBeVisible();
  await page.screenshot({path:'screenshots/09-agent-crew.png'});
  await page.getByRole('button',{name:'Use this crew'}).click();
  await page.getByRole('button',{name:/Start design session/i}).click();
  await expect(page.locator('html')).toHaveAttribute('data-scene-ready','true');
  await expect.poll(async()=>Number((await page.getByTestId('accepted-patches').textContent())?.split('/')[0]?.trim()??0)).toBeGreaterThanOrEqual(2);
  await page.getByLabel('Search components').fill('site/crane/tower-01');
  await expect(page.locator('.component-tree button').first()).toBeVisible();
  await page.getByLabel('Search components').fill('');
  await expect(page.getByTestId('accepted-patches')).toContainText('7 / 7');
  await expect(page.getByTestId('construction-canvas')).toBeVisible();
  await expect.poll(()=>page.evaluate(()=>Boolean((window as any).__SKYFOUNDRY_SCENE__.getObjectByName('cad-planter-import')))).toBe(true);
  expect(await page.evaluate(()=>({lost:(window as any).__SKYFOUNDRY_RENDERER__.getContext().isContextLost(),calls:(window as any).__SKYFOUNDRY_RENDERER__.info.render.calls,triangles:(window as any).__SKYFOUNDRY_RENDERER__.info.render.triangles}))).toMatchObject({lost:false});
  await expect(page.getByText('Configured studio online')).toBeVisible();
  await expect(page.getByTestId('agent-round')).toHaveCount(8);

  const timeline=page.getByLabel('Construction timeline');
  await timeline.fill('160');await page.waitForTimeout(250);
  await page.screenshot({path:'screenshots/02-foundation.png'});
  await timeline.fill('520');await page.waitForTimeout(250);
  await page.screenshot({path:'screenshots/03-structure.png'});
  await timeline.fill('1000');await page.waitForTimeout(500);
  await page.screenshot({path:'screenshots/04-completed-daylight.png'});

  await page.getByLabel('Search components').fill('column/grid-1');
  await page.locator('.component-tree button').first().click();
  await expect(page.getByText('PROVENANCE')).toBeVisible();
  await expect(page.locator('.component-hero code')).toContainText('column/grid-1');
  await page.getByRole('button',{name:'Section X'}).click();
  const pause=page.getByRole('button',{name:'Pause timeline'});if(await pause.isVisible())await pause.click();
  await timeline.fill('430');
  await expect(timeline).toHaveValue('430');
  await page.getByRole('button',{name:'Resume timeline'}).click();
  await page.waitForTimeout(250);
  expect(Number(await timeline.inputValue())).toBeGreaterThan(430);
  await page.screenshot({path:'screenshots/05-section-inspector.png'});

  await page.locator('#revision-input').fill('Make the crown more tapered.');
  await page.getByRole('button',{name:/Preview revision/i}).click();
  await expect(page.getByText('Crown taper study')).toBeVisible();
  await expect(page.getByText(/checks passed/i)).toBeVisible();
  await page.getByRole('button',{name:/Approve & animate/i}).click();
  await expect(page.getByRole('button',{name:/Undo applied revision/i})).toBeVisible();
  await timeline.fill('1000');
  await page.getByRole('button',{name:'Overview'}).click();
  await page.screenshot({path:'screenshots/06-revised-crown.png'});
  await page.getByRole('button',{name:'Close revision preview'}).click();

  await page.getByLabel('Search components').fill('curtain_wall_panel');
  await page.locator('.component-tree button').first().click();
  const demolishedId=await page.locator('.component-hero code').textContent();
  await page.getByRole('button',{name:'Destroy part'}).click();
  await expect(page.getByText(/Demolished tower-a/i)).toBeVisible();
  await page.screenshot({path:'screenshots/10-sandbox-demolition.png'});
  await page.getByRole('button',{name:'Restore last'}).last().click();
  await expect(page.getByText(/Restored the last demolished component/i)).toBeVisible();
  expect(demolishedId).toContain('/facade/');

  await page.getByRole('button',{name:'Replay'}).click();
  const replayPause=page.getByRole('button',{name:'Pause timeline'});if(await replayPause.isVisible())await replayPause.click();
  expect(Number(await timeline.inputValue())).toBeLessThan(250);
  const projectDownload=page.waitForEvent('download');
  await page.getByRole('button',{name:/Export/}).click();
  await page.getByRole('button',{name:'Project JSON'}).click();
  const projectFile=await projectDownload;expect(projectFile.suggestedFilename()).toBe('skyfoundry-manhattan-tower.json');
  const stream=await projectFile.createReadStream();const chunks:Buffer[]=[];for await(const chunk of stream)chunks.push(Buffer.from(chunk));const exported=JSON.parse(Buffer.concat(chunks).toString('utf8'));
  expect(exported.components).toHaveLength(1764);expect(exported.components.some((component:{generator:string})=>component.generator==='cad_extruded_profile')).toBe(true);expect(exported.actions.at(-1).operation.kind).toBe('update_component');

  await page.getByRole('button',{name:/Export/}).click();
  const screenshotDownload=page.waitForEvent('download');
  await page.getByRole('button',{name:'Screenshot PNG'}).click();
  const screenshotFile=await screenshotDownload;expect(screenshotFile.suggestedFilename()).toMatch(/skyfoundry-.*\.png/);expect((await screenshotFile.createReadStream()).readable).toBe(true);
  expect(await page.evaluate(()=>(window as any).__SKYFOUNDRY_RENDERER__.getContext().isContextLost())).toBe(false);
  expect(errors).toEqual([]);
});

test('@visual completed night and mobile viewer',async({browser})=>{
  const page=await browser.newPage({viewport:{width:1440,height:900}});await page.goto('/');await page.getByRole('button',{name:/Start design session/i}).click();await expect(page.locator('html')).toHaveAttribute('data-scene-ready','true');await page.getByLabel('Construction timeline').fill('1000');await page.getByLabel('Scene mode').selectOption('night');await page.waitForTimeout(500);await page.screenshot({path:'screenshots/07-completed-night.png'});await page.getByLabel('Scene mode').selectOption('realistic');await page.getByRole('button',{name:'Street'}).click();await page.waitForTimeout(400);await page.screenshot({path:'screenshots/11-street-context.png'});await page.close();
  const mobile=await browser.newPage({viewport:{width:390,height:844},isMobile:true,hasTouch:true});await mobile.goto('/');await mobile.getByRole('button',{name:/Start design session/i}).click();await expect(mobile.locator('html')).toHaveAttribute('data-scene-ready','true');await mobile.getByLabel('Construction timeline').fill('1000');await mobile.waitForTimeout(300);await mobile.screenshot({path:'screenshots/08-mobile-viewer.png'});await mobile.close();
});
