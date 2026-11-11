"""Validate official JSON schemas and static model/data integrity; not a DAX/M engine."""
import argparse,csv,hashlib,json,re,sys
from pathlib import Path
from urllib.parse import urljoin,urldefrag
from urllib.request import urlopen
from jsonschema import validators,RefResolver
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'powerbi/ClubOps';CACHE=OUT/'schemas'
def main():
 parser=argparse.ArgumentParser()
 parser.add_argument('--fetch-schemas',action='store_true')
 parser.add_argument('--data-dir',type=Path,default=ROOT/'data/processed')
 args=parser.parse_args();fetch=args.fetch_schemas
 CACHE.mkdir(exist_ok=True);manifest_path=CACHE/'manifest.json'
 manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
 documents=[p for p in OUT.rglob('*') if p.suffix in ('.json','.pbip','.pbir','.pbism') and 'schemas' not in p.parts and p.name!='project_spec.json']
 store={}
 def load(url):
  url=urldefrag(url)[0]
  if url in store:return
  filename=hashlib.sha256(url.encode()).hexdigest()+'.json';path=CACHE/filename
  if fetch:
   if not url.startswith('https://developer.microsoft.com/json-schemas/fabric/'):raise ValueError('Unexpected schema host '+url)
   raw=urlopen(url,timeout=30).read();path.write_bytes(raw);manifest[url]={'file':filename,'sha256':hashlib.sha256(raw).hexdigest()}
  elif url not in manifest:raise ValueError('Schema not cached; run --fetch-schemas: '+url)
  raw=path.read_bytes()
  if hashlib.sha256(raw).hexdigest()!=manifest[url]['sha256']:raise ValueError('Schema hash mismatch')
  obj=json.loads(raw);store[url]=obj
  def walk(n):
   if isinstance(n,dict):
    if '$ref' in n and not n['$ref'].startswith('#'):load(urljoin(url,n['$ref']))
    for v in n.values():walk(v)
   elif isinstance(n,list):
    for v in n:walk(v)
  walk(obj)
 for p in documents:load(json.loads(p.read_text())['$schema'])
 manifest_path.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
 for p in documents:
  obj=json.loads(p.read_text());uri=obj['$schema'];s=store[uri]
  # Microsoft schemas declare draft-07; resolve nested relative refs offline.
  cls=validators.validator_for(s);cls.check_schema(s)
  v=cls(s,resolver=RefResolver(base_uri=uri,referrer=s,store=store))
  errors=list(v.iter_errors(obj))
  if errors:raise ValueError(str(p)+': '+str(errors[0]))
 spec=json.loads((OUT/'project_spec.json').read_text());tables={}
 for name,file in spec['csv_files'].items():
  path=args.data_dir/file
  with path.open(encoding='utf-8-sig',newline='') as f:tables[name]=list(csv.DictReader(f))
  if not set(spec['tables'][name]).issubset(tables[name][0]):raise ValueError('CSV schema mismatch')
 tables['DimSeason']=[{'season':s} for s in sorted({r['season'] for r in tables['SeasonSummary']})]
 tables['DimClub']=[dict(club_key=k,club=n) for k,n in sorted({(r['club_key'],r['club']) for r in tables['ClubSummary']})]
 for table,cols in spec['tables'].items():
  content=(OUT/'ClubOps.SemanticModel/definition/tables'/f'{table}.tmdl').read_text()
  actual=dict(re.findall(r'\tcolumn (\w+)\n\t\tdataType: (\w+)',content))
  if actual!=cols or f'partition {table} = m' not in content:raise ValueError('TMDL column/partition mismatch: '+table)
  if table in spec['csv_files'] and ('DataFolder & "'+spec['csv_files'][table]+'"') not in content:raise ValueError('TMDL CSV path mismatch')
 reltext=(OUT/'ClubOps.SemanticModel/definition/relationships.tmdl').read_text()
 for i,(a,b,c,d) in enumerate(spec['relationships']):
  block=f'relationship rel{i}\n\tfromColumn: {a}.{b}\n\ttoColumn: {c}.{d}\n\tfromCardinality: many\n\ttoCardinality: one\n\tcrossFilteringBehavior: oneDirection'
  if block not in reltext:raise ValueError('TMDL relationship differs from checked graph')
 if spec['data_folder'] not in (OUT/'ClubOps.SemanticModel/definition/expressions.tmdl').read_text():raise ValueError('M parameter path mismatch')
 graph={t:[] for t in tables}
 for a,b,c,d in spec['relationships']:
  one=[r[d] for r in tables[c]]
  if len(set(one))!=len(one):raise ValueError('Relationship one-side duplicate')
  if not {r[b] for r in tables[a]}.issubset(set(one)):raise ValueError('Relationship orphan')
  graph[c].append(a)
 for start in graph:
  counts={}
  def visit(n,path):
   if n in path:raise ValueError('Relationship cycle')
   for child in graph[n]:
    counts[child]=counts.get(child,0)+1
    if counts[child]>1:raise ValueError('Ambiguous filter paths')
    visit(child,path+[n])
  visit(start,[])
 for p in documents:
  if p.name!='visual.json':continue
  obj=json.loads(p.read_text())
  for role in obj['visual']['query']['queryState'].values():
   for pr in role['projections']:
    kind=next(iter(pr['field']));f=pr['field'][kind];t=f['Expression']['SourceRef']['Entity'];prop=f['Property']
    if (kind=='Column' and prop not in spec['tables'][t]) or (kind=='Measure' and prop not in spec['measures']):raise ValueError('Unresolved visual field')
 # Static DAX reference resolution; execution/type semantics still require Desktop.
 for name,dax in spec['measures'].items():
  for table,col in re.findall(r'(\w+)\[([^]]+)\]',dax):
   if table not in spec['tables'] or col not in spec['tables'][table]:raise ValueError('Unresolved DAX column')
  for measure in re.findall(r'(?<![\w])\[([^]]+)\]',dax):
   if measure not in spec['measures']:raise ValueError('Unresolved DAX measure')
  if dax.count('(')!=dax.count(')'):raise ValueError('Unbalanced DAX')
  if ("measure '"+name+"' = "+dax) not in (OUT/'ClubOps.SemanticModel/definition/tables/ClubMatches.tmdl').read_text():raise ValueError('TMDL measure mismatch')
 pbip=json.loads((OUT/'ClubOps.pbip').read_text());report=OUT/pbip['artifacts'][0]['report']['path'];link=json.loads((report/'definition.pbir').read_text())
 if (report/link['datasetReference']['byPath']['path']).resolve()!= (OUT/'ClubOps.SemanticModel').resolve():raise ValueError('Model link')
 evidence={'json_documents_validated':len(documents),'official_schemas_cached':len(store),'tables':len(tables),'relationships':len(spec['relationships']),'measures_static_checked':len(spec['measures']),'pages':spec['pages'],'visuals':spec['visual_count'],'csv_counts':{k:len(v) for k,v in tables.items()},'data_folder':spec['data_folder'],'orphan_keys':0,'ambiguous_filter_paths':0,'desktop_tested':False,'tmdl_tom_deserialized':False,'dax_executed':False,'power_query_executed':False,'limits':'JSON/schema, static references and CSV integrity only; visual role semantics, TMDL parsing and DAX/M execution need Desktop.'}
 (ROOT/'artifacts/pbip_verification.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(evidence,indent=2))
if __name__=='__main__':main()
