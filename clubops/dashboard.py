"""Self-contained, offline HTML dashboard preview from validated data exports."""
from __future__ import annotations
import json
from html import escape
from pathlib import Path
from .pipeline import read_csv


def render_html(out_dir: Path) -> str:
    summaries = read_csv(out_dir / "club_summary.csv")
    fixtures = read_csv(out_dir / "club_matches.csv")
    seasons = read_csv(out_dir / "season_summary.csv")
    issues = read_csv(out_dir / "qa_issues.csv")
    if not summaries or not fixtures:
        raise ValueError("Cannot create HTML preview without validated club data")
    data = {"clubs": summaries, "fixtures": fixtures, "seasons": seasons, "issues": issues}
    # Prevent upstream text from closing the inline script tag in a browser.
    payload = json.dumps(data, ensure_ascii=True, separators=(",", ":")).replace("<", "\\u003c").replace(">", "\\u003e")
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<link rel="icon" href="data:,">
<title>ClubOps Intelligence — Fixture dashboard</title>
<style>
:root{font-family:Inter,Segoe UI,Arial,sans-serif;color:#1c2d42;background:#f4f7fa}
*{box-sizing:border-box}body{margin:0}header{background:#11283c;color:white;padding:28px max(24px,calc((100% - 1140px)/2))}
h1{font-size:30px;letter-spacing:-.04em;margin:5px 0 3px}header p{color:#c7d8e2;font-size:13px;margin:8px 0 0}
main{max-width:1160px;margin:0 auto;padding:25px 18px 48px}.tag{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:#62d2cb;font-weight:700}
.notice{background:#e7f4f6;border-left:4px solid #16878a;border-radius:6px;padding:12px 16px;color:#264e57;font-size:13px;line-height:1.5;margin:0 0 20px}
.controls{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:20px}.controls label{display:flex;flex-direction:column;gap:6px;color:#52677b;font-size:12px;font-weight:700}
select{font:inherit;background:white;color:#1c2d42;border:1px solid #cfdbe3;padding:11px 12px;border-radius:8px;min-width:215px}
.cards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-bottom:20px}.card{background:white;border:1px solid #e2e9ef;padding:20px;border-radius:12px;box-shadow:0 3px 14px #19374a0d}
.card .kpi{font-size:32px;font-weight:750;letter-spacing:-.05em;line-height:1.3}.card .label{color:#6d7e8d;font-size:12px;margin-top:4px}
.grid{display:grid;grid-template-columns:1.3fr 1fr;gap:18px}section{background:white;border:1px solid #e2e9ef;border-radius:12px;padding:20px;overflow:hidden}
section h2{font-size:17px;margin:0 0 3px}section p{color:#65798b;font-size:12px;margin:0 0 14px;line-height:1.5}
table{width:100%;border-collapse:collapse;font-size:12px}th{text-align:left;color:#708294;text-transform:uppercase;font-size:10px;letter-spacing:.07em;background:#f4f8fb}th,td{padding:11px 9px;border-bottom:1px solid #ecf0f3}tr:last-child td{border-bottom:0}
.meter{height:9px;border-radius:9px;background:#e4eff0;overflow:hidden}.bar{height:100%;background:#138b8e}.foot{font-size:12px;color:#6f8290;margin-top:18px;line-height:1.65}
@media(max-width:750px){.cards{grid-template-columns:repeat(2,minmax(0,1fr))}.grid{grid-template-columns:1fr}h1{font-size:25px}}
</style></head><body>
<header><div class="tag">Independent portfolio · Public football data</div><h1>The fixture desk.</h1>
<p>Multi-season club fixture reporting, data completeness and briefing-ready insights</p></header>
<main id="main"><div class="notice"><b>Source & scope:</b> Community-maintained Spanish Primera league data (openfootball), not official LALIGA data. League-fixture gaps are not total competitive workload or player rest. This page is an <b>HTML demo, not a Power BI report</b>.</div>
<div class="controls"><label>Season<select id="season" aria-label="Season"></select></label><label>Club<select id="club" aria-label="Club"></select></label></div>
<p id="selection" role="status" aria-live="polite"></p><div class="cards"><div class="card"><div class="kpi" id="fixtures">–</div><div class="label">Listed league fixtures</div></div>
<div class="card"><div class="kpi" id="complete">–</div><div class="label">With final scores</div></div>
<div class="card"><div class="kpi" id="short">–</div><div class="label">League gaps ≤3 days</div></div>
<div class="card"><div class="kpi" id="scorecover">–</div><div class="label">Season result coverage</div></div></div>
<div class="grid"><section><h2>Club fixture log</h2><p>Most recent 12 listed matches in the selected historical season</p><table><thead><tr><th scope="col">Date</th><th scope="col">Opponent</th><th scope="col">Venue</th><th scope="col">Result</th><th scope="col">Gap</th></tr></thead><tbody id="fixtureRows"></tbody></table></section>
<section><h2>Data quality and season coverage</h2><p>Inspect source quality before drawing operational conclusions.</p><table><thead><tr><th scope="col">Metric</th><th scope="col">Value</th></tr></thead><tbody id="qaRows"></tbody></table><h2 style="margin-top:25px">Scored fixture share</h2><p>Coverage of accepted JSON records; not official completeness</p><div class="meter"><div id="meter" class="bar" style="width:0%"></div></div><div class="foot" id="caveat"></div></section></div>
<div class="foot">This dashboard is generated locally from validated CSV files. All metric claims should be reconciled against source hashes, qa_issues.csv and season_summary.csv before publication. No affiliation with LALIGA.</div></main>
<script>
const DATA=__PAYLOAD__;
const $=id=>document.getElementById(id);
const fmt=v=>Number(v||0).toLocaleString('en-GB');
const seasonNames=[...new Set(DATA.seasons.map(s=>s.season))].sort();
function restore(){
  const params=new URLSearchParams(location.search);
  $('season').value=seasonNames.includes(params.get('season'))?params.get('season'):seasonNames.at(-1);
  repopulate(false);
  if([...$('club').options].some(o=>o.value===params.get('club')))$('club').value=params.get('club');
  render(false);
}
function init(){
  $('season').replaceChildren(...seasonNames.map(s=>new Option(s,s)));
  $('season').addEventListener('change',()=>repopulate());
  $('club').addEventListener('change',()=>render());
  addEventListener('popstate',restore);
  restore();
}
function repopulate(sync=true){
  const s=$('season').value;
  const clubs=DATA.clubs.filter(x=>x.season===s).map(x=>x.club).sort((a,b)=>a.localeCompare(b));
  const old=$('club').value;
  $('club').replaceChildren(...clubs.map(x=>new Option(x,x)));
  if(clubs.includes(old))$('club').value=old;
  render(sync);
}
function tableRows(target,rows){
  const body=$(target);body.replaceChildren();
  for(const vals of rows){const tr=document.createElement('tr');for(const val of vals){const td=document.createElement('td');td.textContent=String(val);tr.appendChild(td);}body.appendChild(tr);}
}
function render(sync=true){
  const s=$('season').value,c=$('club').value;
  const summary=DATA.clubs.find(x=>x.season===s&&x.club===c);
  const ss=DATA.seasons.find(x=>x.season===s);
  if(!summary||!ss)return;
  $('selection').textContent=c+' · '+s+' · Historical league fixtures';
  if(sync){
    const url=new URL(location.href);
    url.searchParams.set('season',s);url.searchParams.set('club',c);
    if(url.href!==location.href)history.pushState(null,'',url);
  }
  $('fixtures').textContent=fmt(summary.fixtures);$('complete').textContent=fmt(summary.completed);
  $('short').textContent=fmt(summary.short_gaps_le_3_days);
  $('scorecover').textContent=Number(ss.result_coverage_pct).toFixed(1)+'%';
  const rows=DATA.fixtures.filter(x=>x.season===s&&x.club===c).sort((a,b)=>b.date.localeCompare(a.date)).slice(0,12);
  tableRows('fixtureRows',rows.map(x=>[x.date,x.opponent,x.venue,x.result||'Unscored',x.gap_days_from_previous===''?'—':x.gap_days_from_previous+' d']));
  const issueCount=DATA.issues.filter(x=>x.season===s).length;
  tableRows('qaRows', [['Source records',fmt(ss.source_records)],['Accepted',fmt(ss.accepted)],['Rejected',fmt(ss.rejected)],['Unscored fixtures',fmt(ss.unscored)],['QA messages',fmt(issueCount)],['Benchmark difference (380)',fmt(ss.difference_from_380)]]);
  const pct=Math.max(0,Math.min(100,Number(ss.result_coverage_pct)||0));
  $('meter').style.width=pct+'%';
  $('caveat').textContent='SHA-256: '+ss.source_sha256+' · Benchmark 380 assumes 20 clubs playing home and away; this does not prove source completeness.';
}
init();
</script></body></html>""".replace("__PAYLOAD__", payload)


def write_html(out_dir: Path, target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_html(out_dir), encoding="utf-8")
    return target
