"""Generate the source-controlled PBIP extension from the validated CSV schema."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'powerbi/ClubOps'
BASE='https://developer.microsoft.com/json-schemas/fabric/'
def save(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')
def text(path,value):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(value,encoding='utf-8')
def schema(part):return BASE+'item/report/definition/'+part+'/1.0.0/schema.json'
def main():
 model=OUT/'ClubOps.SemanticModel';report=OUT/'ClubOps.Report';definition=model/'definition'
 save(OUT/'ClubOps.pbip',{'$schema':BASE+'pbip/pbipProperties/1.0.0/schema.json','version':'1.0','artifacts':[{'report':{'path':'ClubOps.Report'}}],'settings':{'enableAutoRecovery':True}})
 save(model/'definition.pbism',{'$schema':BASE+'item/semanticModel/definitionProperties/1.0.0/schema.json','version':'4.0','settings':{}})
 save(report/'definition.pbir',{'$schema':BASE+'item/report/definitionProperties/2.0.0/schema.json','version':'4.0','datasetReference':{'byPath':{'path':'../ClubOps.SemanticModel'}}})
 text(definition/'database.tmdl','database ClubOps\n\tcompatibilityLevel: 1600\n')
 text(definition/'model.tmdl','model Model\n\tculture: en-US\n\tdefaultPowerBIDataSourceVersion: powerBI_V3\n\tsourceQueryCulture: en-US\n')
 folder='C:/CHANGE_ME/clubops-intelligence-public/data/processed/'
 text(definition/'expressions.tmdl',f'expression DataFolder = "{folder}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n')
 files={'Matches':'matches.csv','ClubMatches':'club_matches.csv','ClubSummary':'club_summary.csv','SeasonSummary':'season_summary.csv','QA_Issues':'qa_issues.csv'}
 strings={'season','match_id','round','home','away','home_key','away_key','source_sha256','source_url','club','club_key','opponent','venue','result','severity','code','detail'}
 specs={};measures={
 'Club Fixtures':'COUNTROWS(ClubMatches)', 'Club Scored':'SUM(ClubMatches[is_complete])',
 'Club Unknown':'[Club Fixtures] - [Club Scored]',
 'League Matches':'DISTINCTCOUNT(ClubMatches[match_id])',
 'Wins':'CALCULATE(COUNTROWS(ClubMatches), ClubMatches[result] = "W")',
 'Short League Gaps':'COUNTROWS(FILTER(ClubMatches, NOT ISBLANK(ClubMatches[gap_days_from_previous]) && ClubMatches[gap_days_from_previous] <= 3))',
 'Average League Gap':'AVERAGE(ClubMatches[gap_days_from_previous])',
 'Peer Short Gaps':'CALCULATE([Short League Gaps], REMOVEFILTERS(DimClub))',
 'Source Records':'SUM(SeasonSummary[source_records])', 'Accepted Records':'SUM(SeasonSummary[accepted])',
 'Rejected Records':'SUM(SeasonSummary[rejected])','Unknown Results':'SUM(SeasonSummary[unscored])',
 'Result Coverage':'DIVIDE(SUM(SeasonSummary[completed]), SUM(SeasonSummary[accepted]))',
 'QA Messages':'COALESCE(COUNTROWS(QA_Issues), 0)'}
 for table,file in files.items():
  with (ROOT/'data/processed'/file).open(encoding='utf-8-sig',newline='') as f:headers=next(csv.reader(f))
  cols={h:('string' if h in strings else 'dateTime' if h=='date' else 'double' if h in ('average_gap_days','result_coverage_pct') else 'int64') for h in headers};specs[table]=cols
 specs['DimSeason']={'season':'string'};specs['DimClub']={'club_key':'string','club':'string'}
 for table,cols in specs.items():
  lines=['table '+table]
  for col,typ in cols.items():
   lines+=['',f'\tcolumn {col}',f'\t\tdataType: {typ}','\t\tsummarizeBy: none',f'\t\tsourceColumn: {col}']
   if typ=='dateTime':lines+=['\t\tformatString: yyyy-MM-dd']
  if table=='ClubMatches':
   for name,dax in measures.items():
    fmt='0.00%' if name=='Result Coverage' else '0.00' if name=='Average League Gap' else '#,0'
    lines+=['',f"\tmeasure '{name}' = {dax}",f'\t\tformatString: {fmt}']
  if table in files:
   types=', '.join('{"'+c+'", '+('type text' if t=='string' else 'type date' if t=='dateTime' else 'type number' if t=='double' else 'Int64.Type')+'}' for c,t in cols.items())
   nums=', '.join('"'+c+'"' for c,t in cols.items() if t in ('int64','double'))
   source=f'let\n    Raw = Csv.Document(File.Contents(DataFolder & "{files[table]}"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),\n    Headers = Table.PromoteHeaders(Raw, [PromoteAllScalars=true]),\n    Nulls = Table.ReplaceValue(Headers, "", null, Replacer.ReplaceValue, {{{nums}}}),\n    Typed = Table.TransformColumnTypes(Nulls, {{{types}}}, "en-US")\nin\n    Typed'
  elif table=='DimSeason':source='Table.Distinct(Table.SelectColumns(SeasonSummary, {"season"}))'
  else:source='Table.Distinct(Table.SelectColumns(ClubSummary, {"club_key", "club"}))'
  lines+=['',f'\tpartition {table} = m','\t\tmode: import','\t\tsource =']+['\t\t\t'+l for l in source.splitlines()]
  text(definition/'tables'/f'{table}.tmdl','\n'.join(lines)+'\n')
 relationships=[('Matches','season','DimSeason','season'),('ClubMatches','match_id','Matches','match_id'),('ClubSummary','season','DimSeason','season'),('SeasonSummary','season','DimSeason','season'),('QA_Issues','season','DimSeason','season'),('ClubMatches','club_key','DimClub','club_key'),('ClubSummary','club_key','DimClub','club_key')]
 text(definition/'relationships.tmdl','\n'.join(f'relationship rel{i}\n\tfromColumn: {a}.{b}\n\ttoColumn: {c}.{d}\n\tfromCardinality: many\n\ttoCardinality: one\n\tcrossFilteringBehavior: oneDirection\n' for i,(a,b,c,d) in enumerate(relationships)))
 rd=report/'definition'
 save(rd/'version.json',{'$schema':schema('versionMetadata'),'version':'2.0.0'})
 save(rd/'report.json',{'$schema':schema('report'),'layoutOptimization':'None','themeCollection':{}})
 names=['ClubOverview','FixtureOperations','DataQuality'];save(rd/'pages/pages.json',{'$schema':schema('pagesMetadata'),'pageOrder':names,'activePageName':names[0]})
 visual_count=0
 def projection(table,prop,measure=False):
  kind='Measure' if measure else 'Column'
  return {'field':{kind:{'Expression':{'SourceRef':{'Entity':table}},'Property':prop}},'queryRef':table+'.'+prop}
 def visual(page,kind,title,x,y,w,h,roles):
  nonlocal visual_count
  visual_count+=1;name=f'visual{visual_count:03}'
  obj={'$schema':schema('visualContainer'),'name':name,'position':{'x':x,'y':y,'width':w,'height':h,'z':visual_count,'tabOrder':visual_count},'visual':{'visualType':kind,'query':{'queryState':{role:{'projections':[projection(*field) for field in fields]} for role,fields in roles.items()}},'visualContainerObjects':{'title':[{'properties':{'show':{'expr':{'Literal':{'Value':'true'}}},'text':{'expr':{'Literal':{'Value':"'"+title+"'"}}}}}]}}}
  save(rd/'pages'/page/'visuals'/name/'visual.json',obj)
 for page,title in zip(names,['Club Overview','Fixture & Operations Analytics','Data Quality']):
  save(rd/'pages'/page/'page.json',{'$schema':schema('page'),'name':page,'displayName':title,'displayOption':'FitToPage','width':1280,'height':800})
  visual(page,'slicer','Season',20,10,250,90,{'Values':[('DimSeason','season')]})
  if page!='DataQuality':visual(page,'slicer','Club',290,10,350,90,{'Values':[('DimClub','club')]})
  cards=['Club Fixtures','Club Scored','Club Unknown','Wins'] if page=='ClubOverview' else ['Short League Gaps','Average League Gap','League Matches'] if page=='FixtureOperations' else ['Source Records','Accepted Records','Unknown Results','Result Coverage']
  for i,m in enumerate(cards):visual(page,'card',m,20+310*i,115,295,115,{'Values':[('ClubMatches',m,True)]})
  if page=='ClubOverview':
   visual(page,'clusteredColumnChart','Listed league fixtures by club',20,250,610,280,{'Category':[('DimClub','club')],'Y':[('ClubMatches','Club Fixtures',True)]})
   fields=[('ClubMatches',c) for c in ['date','opponent','venue','result','gap_days_from_previous']]
   visual(page,'tableEx','Dated league fixture log (unknown result = blank)',650,250,610,500,{'Values':fields})
  elif page=='FixtureOperations':
   visual(page,'clusteredColumnChart','Short league gaps by club - calendar intervals, not physical rest',20,250,1240,260,{'Category':[('DimClub','club')],'Y':[('ClubMatches','Short League Gaps',True)]})
   visual(page,'tableEx','League only; excludes cup and European workload',20,530,1240,240,{'Values':[('ClubMatches',c) for c in ['date','club','opponent','venue','gap_days_from_previous']]})
  else:
   visual(page,'clusteredColumnChart','QA messages by category',20,250,450,250,{'Category':[('QA_Issues','code')],'Y':[('ClubMatches','QA Messages',True)]})
   visual(page,'tableEx','Community data - 380 benchmark does not certify results',490,250,770,250,{'Values':[('SeasonSummary',c) for c in ['season','source_records','accepted','rejected','completed','unscored','result_coverage_pct']]})
   visual(page,'tableEx','Warnings/rejections with source row traceability',20,520,1240,250,{'Values':[('QA_Issues',c) for c in ['season','severity','source_row','code','detail']]})
 save(OUT/'project_spec.json',{'tables':specs,'csv_files':files,'relationships':relationships,'measures':measures,'pages':names,'visual_count':visual_count,'data_folder':folder})
 print('Generated PBIP: 7 TMDL tables, 14 DAX measures, 7 relationships, 3 PBIR pages,',visual_count,'visuals')
if __name__=='__main__':main()
