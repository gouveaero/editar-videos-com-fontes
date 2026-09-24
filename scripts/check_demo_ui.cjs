/* Click/input checks for the fixture created by check_editorial.py, in a fresh
   headless browser. Pass local puppeteer-core path, Chrome path, QA project path. */
const fs=require('fs'),path=require('path'),assert=require('assert');
(async()=>{
 const puppeteer=require(process.argv[2]);const project=path.resolve(process.argv[4]);const root=path.dirname(project);
 const built=JSON.parse(fs.readFileSync(path.join(root,'build/build.json'))).components;
 const browser=await puppeteer.launch({executablePath:process.argv[3],headless:'shell',timeout:15000,protocolTimeout:15000,args:['--allow-file-access-from-files','--disable-gpu']});
 try{
  console.log('Browser ready');
  const page=await browser.newPage();await page.setViewport({width:1080,height:1920});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('file://'+path.join(built['01_principal'].folder,'index.html'),{waitUntil:'domcontentloaded',timeout:15000});console.log('Composition loaded');
  await page.evaluate(()=>{window.__timelines.main.seek(6.5,false);});
  await page.click('#ev4 [data-next="b"]');
  assert.equal(await page.$eval('#ev4 [data-state="b"]',e=>e.style.opacity),'1');
  assert.equal(await page.$eval('#ev4 [data-state="a"]',e=>e.style.pointerEvents),'none');
  await page.click('#ev4 [data-next="a"]');assert.equal(await page.$eval('#ev4 [data-state="a"]',e=>e.style.opacity),'1');
  await page.evaluate(()=>{window.__timelines.main.seek(9.5,false);});
  await page.$eval('#ev5 input',e=>{e.value='2';e.dispatchEvent(new Event('input',{bubbles:true}));});
  assert.equal(await page.$eval('#ev5 .ev-period',e=>e.textContent),'2,84 s');
  await page.evaluate(()=>{window.__timelines.main.seek(12.5,false);});await page.click('#ev6 [data-event="b"]');
  assert.equal(await page.$eval('#ev6 [data-document="b"]',e=>e.style.opacity),'1');
  const link=await page.$eval('#ev6 [data-document="b"] a',e=>e.href);const documentPage=await browser.newPage();await documentPage.goto(link);
  assert.match(await documentPage.$eval('h1',e=>e.textContent),/Documento fictício 2/);await documentPage.close();
  await page.evaluate(()=>{window.__timelines.main.seek(9.5,false);});assert.equal(await page.$eval('#ev5 .ev-length',e=>e.textContent),'1,0 m');
  const overflows=await page.evaluate(()=>Array.from(document.querySelectorAll('.ev-doc,.ev-state')).filter(e=>e.scrollHeight>e.clientHeight+1).map(e=>e.className));
  assert.deepEqual(errors,[]);assert.deepEqual(overflows,[]);
  const result={ok:true,checks:['actual pointer click opens and returns to prototype states','invisible panels cannot intercept clicks','range input updates physical period','event click selects linked document','linked local document loads','backward seek restores simulation state','no browser errors or overflowing panels']};
  fs.writeFileSync(path.join(root,'ui-checks.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
 }finally{browser.process()?.kill('SIGTERM');browser.disconnect();}
})().catch(e=>{console.error(e);process.exit(1);});
