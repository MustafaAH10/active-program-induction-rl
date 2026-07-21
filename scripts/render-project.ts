import { chromium } from '@playwright/test';
import { mkdir } from 'node:fs/promises';
const base=process.env.SKYFOUNDRY_URL??'http://127.0.0.1:3000';const out=process.argv[2]??'screenshots/completed-daylight.png';
await mkdir(out.split('/').slice(0,-1).join('/')||'.',{recursive:true});const browser=await chromium.launch({channel:'chrome'});const page=await browser.newPage({viewport:{width:1600,height:1000},deviceScaleFactor:1});await page.goto(base);await page.getByRole('button',{name:/Start design session/i}).click();await page.locator('html[data-scene-ready="true"]').waitFor();await page.getByLabel('Construction timeline').fill('1000');await page.waitForTimeout(600);await page.screenshot({path:out});await browser.close();console.log(`Captured ${out}`);

