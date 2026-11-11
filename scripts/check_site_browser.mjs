// Run: node --experimental-websocket scripts/check_site_browser.mjs [--local]
// Uses installed Chrome and its debugging protocol; no browser dependency install.
import {spawn} from 'node:child_process';
import {readFileSync,existsSync,mkdirSync,writeFileSync} from 'node:fs';
import {resolve,dirname,join,extname} from 'node:path';
import {fileURLToPath} from 'node:url';
import http from 'node:http';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const local=process.argv.includes('--local');
const pause=ms=>new Promise(r=>setTimeout(r,ms));
const ensure=(ok,msg)=>{if(!ok)throw new Error(msg)};
let server;
let base='https://mrtrauf.github.io/clubops-intelligence-public/';
if(local){
  const site=join(root,'site');
  server=http.createServer((req,res)=>{
    let path=resolve(site,'.'+decodeURIComponent(new URL(req.url,'http://test.invalid').pathname));
    if(!path.startsWith(site)){res.writeHead(403);return res.end()}
    if(!extname(path))path=join(path,'index.html');
    try{const types={'.html':'text/html; charset=utf-8','.css':'text/css','.png':'image/png','.json':'application/json','.csv':'text/csv','.xlsx':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','.zip':'application/zip'};res.setHeader('Content-Type',types[extname(path)]||'text/plain');res.end(readFileSync(path))}catch{res.writeHead(404);res.end('Not found')}
  });
  await new Promise(r=>server.listen(0,'127.0.0.1',r));
  base=`http://127.0.0.1:${server.address().port}/`;
}
const runtime=join(root,'.runtime',`pages-browser-${Date.now()}`);mkdirSync(runtime,{recursive:true});
const chrome=process.env.CHROME_PATH || (process.platform==='win32' ? join(process.env.PROGRAMFILES||'C:/Program Files','Google/Chrome/Application/chrome.exe') : '/usr/bin/chromium');
ensure(existsSync(chrome),'Installed Chrome not found');
const child=spawn(chrome,['--headless','--disable-gpu','--no-sandbox','--no-first-run','--remote-debugging-port=0','--remote-allow-origins=*',`--user-data-dir=${runtime}`,'about:blank'],{stdio:'ignore',windowsHide:true});
let ws;
try{
  const active=join(runtime,'DevToolsActivePort');
  for(let n=0;n<100&&!existsSync(active);n++)await pause(100);
  ensure(existsSync(active),'Chrome did not start');
  const port=readFileSync(active,'utf8').split('\n')[0];
  const targets=await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  ws=new WebSocket(targets.find(t=>t.type==='page').webSocketDebuggerUrl);
  await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j});
  let next=0;const pending=new Map(),errors=[],httpErrors=[];
  ws.onmessage=event=>{
    const m=JSON.parse(event.data);
    if(m.id){const p=pending.get(m.id);if(p){pending.delete(m.id);m.error?p.reject(new Error(JSON.stringify(m.error))):p.resolve(m.result)}}
    if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text);
    if(m.method==='Runtime.consoleAPICalled'&&m.params.type==='error')errors.push(JSON.stringify(m.params.args));
    if(m.method==='Log.entryAdded'&&m.params.entry.level==='error')errors.push(m.params.entry.text);
    if(m.method==='Network.responseReceived'&&m.params.response.status>=400)httpErrors.push({url:m.params.response.url,status:m.params.response.status});
  };
  const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++next;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));setTimeout(()=>{if(pending.has(id)){pending.delete(id);reject(new Error('CDP timeout '+method))}},20000).unref()});
  const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});ensure(!r.exceptionDetails,'JS evaluation failed: '+JSON.stringify(r.exceptionDetails));return r.result.value};
  for(const method of ['Page.enable','Runtime.enable','Log.enable','Network.enable'])await send(method);
  const waitFor=async expression=>{for(let n=0;n<100;n++){if(await evaluate(expression))return;await pause(100)}throw new Error('Page readiness failed: '+expression)};
  const navigate=async path=>{await send('Page.navigate',{url:new URL(path,base).href});await waitFor('document.readyState==="complete"');await evaluate('document.fonts.ready.then(()=>true)');await pause(200)};
  const viewport=async(width,height)=>{await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<600});await pause(200)};
  const captures=local?runtime:join(root,'artifacts/screenshots');mkdirSync(captures,{recursive:true});
  const snapshot=async name=>{const shot=await send('Page.captureScreenshot',{format:'png'});writeFileSync(join(captures,name),Buffer.from(shot.data,'base64'))};
  await viewport(1440,1000);await navigate('index.html');
  await waitFor('document.querySelector("h1")?.textContent.includes("fixture calendar")');
  await evaluate('document.querySelectorAll("img").forEach(x=>x.loading="eager")');
  await waitFor('[...document.images].every(x=>x.complete&&x.naturalWidth>0)');
  ensure(await evaluate('document.documentElement.scrollWidth<=innerWidth'),'Desktop landing overflows');
  await snapshot('Website_Desktop.png');
  await viewport(390,844);
  ensure(await evaluate('document.documentElement.scrollWidth<=innerWidth'),'Mobile landing overflows');
  await snapshot('Website_Mobile.png');
  await evaluate('document.querySelector(".actions a").click()');
  await waitFor('document.querySelector("#fixtures")?.textContent==="38"');
  const views=[];
  const metrics=async(season,club,expected)=>{
    await evaluate(`document.getElementById('season').value=${JSON.stringify(season)};document.getElementById('season').dispatchEvent(new Event('change'));document.getElementById('club').value=${JSON.stringify(club)};document.getElementById('club').dispatchEvent(new Event('change'));`);
    const values=await evaluate("['fixtures','complete','short','scorecover'].map(id=>document.getElementById(id).textContent)");
    ensure(JSON.stringify(values)===JSON.stringify(expected),'Dashboard mismatch '+season+' '+club+' '+values);
    ensure(await evaluate('document.querySelectorAll("#fixtureRows tr").length===12'),'Fixture table row count');
    views.push({season,club,values});
  };
  await metrics('2024-25','FC Barcelona',['38','37','7','97.4%']);
  ensure(await evaluate('document.documentElement.scrollWidth<=innerWidth'),'Mobile dashboard overflows');
  await snapshot('Dashboard_Mobile.png');
  await viewport(1440,1000);
  await snapshot('Dashboard_Desktop.png');
  await metrics('2023-24','FC Barcelona',['38','38','5','100.0%']);
  ensure(await evaluate('new URLSearchParams(location.search).get("season")==="2023-24"'),'Season missing from share URL');
  ensure(await evaluate('new URLSearchParams(location.search).get("club")==="FC Barcelona"'),'Club missing from share URL');
  await send('Page.reload');await waitFor('document.readyState==="complete"');
  await waitFor('document.getElementById("short")?.textContent==="5"');

  await metrics('2024-25','Real Madrid CF',['38','37','6','97.4%']);
  await metrics('2023-24','Girona FC',['38','38','2','100.0%']);
  await metrics('2024-25','Valencia CF',['38','37','3','97.4%']);
  await evaluate('history.back()');
  await waitFor('document.getElementById("club").value==="Girona FC"');
  ensure(await evaluate('document.getElementById("short").textContent===DATA.clubs.find(x=>x.club===document.getElementById("club").value&&x.season===document.getElementById("season").value).short_gaps_le_3_days'),'Back did not restore metrics');

  await navigate('dashboard/?season=invalid&club=invalid');
  await waitFor('document.getElementById("fixtures")?.textContent==="38"');
  ensure(await evaluate('document.getElementById("season").value==="2024-25"'),'Invalid season fallback failed');
  await evaluate('document.getElementById("season").focus()');
  await send('Input.dispatchKeyEvent',{type:'keyDown',key:'ArrowUp',code:'ArrowUp',windowsVirtualKeyCode:38});
  await send('Input.dispatchKeyEvent',{type:'keyUp',key:'ArrowUp',code:'ArrowUp',windowsVirtualKeyCode:38});
  await waitFor('document.getElementById("season").value==="2023-24"');
  ensure(await evaluate('document.activeElement.id==="season"'),'Filter focus lost');
  await evaluate('document.querySelector("header a").click()');
  await waitFor('document.querySelector(".hero")!==null');
  // Follow the release visitor journey using real links.
  await evaluate(`document.querySelector('nav a[href="case-study.html"]').click()`);
  await waitFor('document.querySelector("h1")?.textContent.includes("Historical calendars")');
  await evaluate('document.querySelectorAll("img").forEach(x=>x.loading="eager")');
  await waitFor('[...document.images].every(x=>x.complete&&x.naturalWidth>0)');
  await evaluate(`document.querySelector('main a[href="dashboard/"]').click()`);
  await waitFor('document.getElementById("fixtures")?.textContent==="38"');
  await evaluate(`document.querySelector('nav a[href="../briefing.html"]').click()`);
  await waitFor('document.querySelector(".brief-stats strong")?.textContent==="25"');
  ensure(await evaluate('document.querySelectorAll("tbody")[0].rows.length===4 && document.querySelectorAll("tbody")[1].rows.length===5'),'Briefing fixture counts');
  await evaluate('document.querySelector("summary").focus()');
  await send('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter',windowsVirtualKeyCode:13,text:'\r'});
  await send('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});
  await waitFor('document.querySelector("details").open');
  ensure(await evaluate('document.querySelector("details").textContent.includes("da5bfa1b3634e1039d9e71aec50bdc847f8761189e3de235a4e730e0dc64ca38")'),'Source hash missing');
  await evaluate(`document.querySelector('main a[href="index.html"]').click()`);
  await waitFor('document.querySelector(".hero")!==null');
  for(const width of [1440,768,390,320]){
    await viewport(width,width===1440?1000:844);
    for(const [path,name] of [['case-study.html','Case_Study'],['briefing.html','Briefing']]){
      await navigate(path);
      await evaluate('document.querySelectorAll("img").forEach(x=>x.loading="eager")');
      await waitFor('[...document.images].every(x=>x.complete&&x.naturalWidth>0)');
      ensure(await evaluate('document.documentElement.scrollWidth<=innerWidth'),path+' overflows at '+width);
      ensure(await evaluate('document.querySelectorAll("h1").length===1 && document.querySelector("main").firstElementChild!==null'),'Heading structure missing');
      if(width===1440||width===390)await snapshot(name+(width===1440?'_Desktop.png':'_Mobile.png'));
      if(width===390){
        await evaluate(path==='briefing.html' ? 'document.querySelector(".table-scroll").scrollIntoView()' : 'document.querySelector(".findings").scrollIntoView()');
        await snapshot(name+'_Detail_Mobile.png');
      }
    }
  }
  ensure(!errors.length&&!httpErrors.length,'Browser errors: '+JSON.stringify({errors,httpErrors}));
  const result={base,mode:local?'local preview':'live public HTTPS',views,viewport_checks:[1440,768,390,320],visitor_journey:'homepage -> case study -> dashboard -> briefing -> homepage',live_change_events:true,images_loaded:true,console_errors:errors,http_errors:httpErrors,manual_accessibility_certification:false};
  writeFileSync(local?join(runtime,'verification.json'):join(root,'artifacts/site_browser_verification.json'),JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify(result,null,2));
  await send('Browser.close').catch(()=>{});
}finally{if(ws)ws.close();child.kill();if(server)server.close()}
