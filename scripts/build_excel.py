"""Populate the preserved starter; native pivot/calculation is a separate Excel step.

Optional reporting dependency: openpyxl. Core CLI remains standard-library only.
"""
import csv
import json
from pathlib import Path
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.table import Table, TableStyleInfo

ROOT = Path(__file__).resolve().parents[1]


def main():
    template = load_workbook(ROOT / 'excel/ClubOps_Excel_Starter.xlsx')
    # Preserve the starter sheet structure and keep its original file untouched.
    wb = Workbook()
    wb.remove(wb.active)
    for name in template.sheetnames:
        wb.create_sheet(name)
    for name, filename, table_name in [('Season Summary','season_summary.csv','SeasonData'),
                                       ('Club Summary','club_summary.csv','ClubData'),
                                       ('QA Issues','qa_issues.csv','QAIssues')]:
        ws = wb[name] if name in wb.sheetnames else wb.create_sheet(name)
        with (ROOT / 'data/processed' / filename).open(encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            ws.append(headers)
            numeric = set(headers) - {'season','club','club_key','source_sha256','severity','code','detail'}
            for row in reader:
                ws.append([float(row[k]) if k in numeric and row[k] else row[k] for k in headers])
        table = Table(displayName=table_name, ref=ws.dimensions)
        table.tableStyleInfo = TableStyleInfo(name='TableStyleMedium2', showRowStripes=True)
        ws.add_table(table)
    ws = wb['Overview']
    for row in [
        ['CLUBOPS INTELLIGENCE', 'Independent portfolio | 11 November 2026'],
        ['League fixture reporting', 'Public community data; no LALIGA affiliation'],
        [], ['Metric','Value','Meaning'],
        ['Seasons','=COUNTA(SeasonData[season])','Pinned input files'],
        ['Listed fixtures','=SUM(SeasonData[accepted])','Match grain, not club-match rows'],
        ['Scored fixtures','=SUM(SeasonData[completed])','Known full-time scores'],
        ['Unscored fixtures','=SUM(SeasonData[unscored])','Unknown results, never treated as draws'],
        ['Result coverage','=B7/B6','Share of accepted fixtures with final scores'],
        ['Rejected rows','=SUM(SeasonData[rejected])','See QA Issues and retained raw records'],
        [], ['Club focus','FC Barcelona'], ['Season focus','2024-25'],
        ['Fixtures','=SUMIFS(ClubData[fixtures],ClubData[club],B12,ClubData[season],B13)'],
        ['Scored','=SUMIFS(ClubData[completed],ClubData[club],B12,ClubData[season],B13)'],
        ['Wins','=SUMIFS(ClubData[wins],ClubData[club],B12,ClubData[season],B13)'],
        ['Short league gaps <=3 days','=SUMIFS(ClubData[short_gaps_le_3_days],ClubData[club],B12,ClubData[season],B13)'],
        [], ['Coverage warning','2024-25: Matchday 38 has ten unknown results.'],
        ['Gap interpretation','Calendar gaps between league fixtures; not physical rest.'],
        ['As-of briefing','Retrospective reconstruction, not an archived schedule.'],
        ['Refresh','Run pipeline, then build_excel.py and complete_excel.ps1.'],
        ['Power Query alternative','See docs/EXCEL_SETUP.md; no embedded query claimed.'],
        ['Pivot status','Created and checked only by complete_excel.ps1.'],
    ]:
        ws.append(row)
    ws['B9'].number_format = '0.00%'
    manifest = json.loads((ROOT / 'data/provenance/manifest.json').read_text())
    ws = wb['Sources & QA']
    with (ROOT / 'data/processed/season_summary.csv').open(encoding='utf-8-sig', newline='') as stream:
        season_rows = list(csv.DictReader(stream))
    with (ROOT / 'data/processed/qa_issues.csv').open(encoding='utf-8-sig', newline='') as stream:
        qa_rows = list(csv.DictReader(stream))
    accounting = '; '.join(f"{s['season']}: {s['source_records']} raw / {s['accepted']} accepted / {s['rejected']} rejected" for s in season_rows)
    for row in [['SOURCE AND QUALITY REGISTER'], ['Upstream commit',manifest['commit']],
                ['Acquired / verified UTC',manifest['verified_at_utc']],
                ['License','CC0 1.0; retained in data/provenance/LICENSE.md'],
                ['Aliases','See configs/aliases.json; exact source names preserved unless reviewed'],
                ['Raw accounting',accounting],
                ['QA',f'{len(qa_rows)} ledger entries; see QA Issues'],
                ['Source authority','Community-maintained; not official LALIGA data'],
                ['Source limitation','No cup/European fixtures, player rest, attendance or finance'],
                ['Unknown result policy','Unscored records contribute to fixtures and gaps, never W/D/L']]:
        ws.append(row)
    for src in manifest['sources']:
        ws.append([src['season']+' URL',src['pinned_url']])
        ws.append([src['season']+' SHA-256',src['sha256']])
    wb.create_sheet('Club Pivot')
    for ws in wb:
        ws.sheet_view.showGridLines = False
        ws.freeze_panes = 'A2'
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.page_setup.orientation = 'landscape'
        ws.page_setup.paperSize = ws.PAPERSIZE_A4
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 1
        for cell in ws[1]:
            cell.fill = PatternFill('solid', fgColor='11283C')
            cell.font = Font(color='FFFFFF', bold=True, size=12)
        ws.row_dimensions[1].height = 30
        for col in ws.columns:
            letter = col[0].column_letter
            width = max(len(str(c.value or '')) if c.data_type != 'f' else 15 for c in col)
            ws.column_dimensions[letter].width = min(max(width+2, 14), 48)
            for c in col[1:]:
                c.alignment = Alignment(vertical='center', wrap_text=True)
                c.font = Font(name='Calibri', size=11, color='1C2D42')
        if ws.title in ('Overview','Sources & QA'):
            ws.column_dimensions['A'].width = 32
            ws.column_dimensions['B'].width = 26 if ws.title == 'Overview' else 78
            ws.column_dimensions['C'].width = 72
            for r in range(2,ws.max_row+1):
                ws.row_dimensions[r].height = 24
        if ws.title == 'Overview':
            for r in (1,2,19,20,21,22,23,24):
                ws.merge_cells(start_row=r,start_column=2,end_row=r,end_column=3)
    target = ROOT / 'artifacts/ClubOps_Reporting_COMPLETED.xlsx'
    target.parent.mkdir(exist_ok=True)
    wb.save(target)
    print(f'Populated {target.name}; native Excel calculation and pivot verification PENDING')


if __name__ == '__main__':
    main()
