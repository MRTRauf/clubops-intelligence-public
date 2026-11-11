$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$path = Join-Path $repo 'artifacts\ClubOps_Reporting_COMPLETED.xlsx'
$excel = New-Object -ComObject Excel.Application
$excel.DisplayAlerts = $false
$excel.Visible = $false
$book = $null
try {
    $template = $excel.Workbooks.Open((Join-Path $repo 'excel\ClubOps_Excel_Starter.xlsx'), 0, $true)
    $template.Close($false)
    $book = $excel.Workbooks.Open($path)
    $data = $book.Worksheets.Item('Club Summary')
    $sheet = $book.Worksheets.Item('Club Pivot')
    $cache = $book.PivotCaches().Create(1, 'ClubData')
    $pivot = $cache.CreatePivotTable($sheet.Range('A3'), 'ClubSeasonPivot')
    $pivot.PivotFields('club').Orientation = 1
    $pivot.PivotFields('season').Orientation = 2
    $captions = @{fixtures='Club fixtures'; completed='Scored'; short_gaps_le_3_days='Gaps <=3 days'}
    foreach ($field in @('fixtures','completed','short_gaps_le_3_days')) {
        [void]$pivot.AddDataField($pivot.PivotFields($field), $captions[$field], -4157)
    }
    $sheet.Range('A1').Value2 = 'CLUB / SEASON ANALYSIS - native Excel PivotTable'
    $sheet.Range('A1').Font.Bold = $true
    $pivot.TableStyle2 = 'PivotStyleMedium9'
    $pivot.RowGrand = $false
    $pivot.ColumnGrand = $false
    $sheet.Range('A2').Value2 = 'Per club / season. Grand totals suppressed; distinct league matches appear on Season Summary.'
    [void]$pivot.RefreshTable()
    [void]$sheet.UsedRange.Columns.AutoFit()
    $sheet.Columns.Item(1).ColumnWidth = 32
    $sheet.Range('B:G').ColumnWidth = 18
    $sheet.Rows.Item(5).RowHeight = 28
    $sheet.Range('A1:G1').Merge()
    $sheet.Range('A2:G2').Merge()
    $sheet.Range('A2').WrapText = $true
    $sheet.Rows.Item(2).RowHeight = 30
    $excel.CalculateFullRebuild()
    $overview = $book.Worksheets.Item('Overview')
    $seasons = @(Import-Csv (Join-Path $repo 'data\processed\season_summary.csv'))
    $expected = @{ B5=$seasons.Count; B6=($seasons | Measure-Object accepted -Sum).Sum;
      B7=($seasons | Measure-Object completed -Sum).Sum; B8=($seasons | Measure-Object unscored -Sum).Sum;
      B10=($seasons | Measure-Object rejected -Sum).Sum }
    $checks = @()
    foreach ($cell in $expected.Keys) {
        $actual = $overview.Range($cell).Value2
        if ($actual -ne $expected[$cell]) { throw "Formula $cell expected $($expected[$cell]), got $actual" }
        $checks += @{cell=$cell; expected=$expected[$cell]; actual=$actual; formula=$overview.Range($cell).Formula}
    }
    if ([Math]::Abs($overview.Range('B9').Value2 - ($expected.B7/$expected.B6)) -gt 0.000001) { throw 'Coverage formula mismatch' }
    $rows = Import-Csv (Join-Path $repo 'data\processed\club_summary.csv')
    $pivotChecks = @()
    foreach ($row in $rows) {
        foreach ($field in @('fixtures','completed','short_gaps_le_3_days')) {
            $actual = $pivot.GetPivotData($captions[$field], 'club', $row.club, 'season', $row.season).Value2
            if ($actual -ne [double]$row.$field) { throw "Pivot mismatch $($row.season) $($row.club) $field" }
            $pivotChecks += @{season=$row.season; club=$row.club; field=$field; actual=$actual; expected=[double]$row.$field}
        }
    }
    $focus = $rows | Where-Object { $_.club -eq 'FC Barcelona' -and $_.season -eq '2024-25' }
    foreach ($pair in @(@('B14','fixtures'),@('B15','completed'),@('B16','wins'),@('B17','short_gaps_le_3_days'))) {
        if ($overview.Range($pair[0]).Value2 -ne [double]$focus.($pair[1])) { throw 'SUMIFS focus mismatch' }
    }
    $overview.Range('B24').Value2 = 'Native PivotTable created, refreshed and reconciled in Excel.'
    # Exercise season focus formulas before restoring the requested demonstration.
    $overview.Range('B13').Value2 = '2023-24'
    $excel.CalculateFullRebuild()
    if ($overview.Range('B15').Value2 -ne 38) { throw 'Season focus change failed' }
    $overview.Range('B13').Value2 = '2024-25'
    $excel.CalculateFullRebuild()
    $overview.Activate()
    $excel.ActiveWindow.Zoom = 70
    $book.Save()
    $book.Close($true)
    $book = $excel.Workbooks.Open($path, 0, $true)
    if ($book.Worksheets.Item('Club Pivot').PivotTables().Count -ne 1) { throw 'Saved pivot did not reopen' }
    $savedPivot = $book.Worksheets.Item('Club Pivot').PivotTables(1)
    if ($savedPivot.RowGrand -or $savedPivot.ColumnGrand) { throw 'Pivot grand totals must stay suppressed' }
    foreach ($caption in $captions.Values) {
        if ($savedPivot.DataFields($caption).Caption -ne $caption) { throw 'Saved pivot caption mismatch' }
    }
    if ($book.Worksheets.Item('Club Pivot').Range('B5').ColumnWidth -lt 18) { throw 'Pivot column width failed' }
    if ($book.Worksheets.Item('Overview').Range('B6').Value2 -ne $expected.B6) { throw 'Saved formula cache failed' }
    $book.Worksheets.Item('Overview').ExportAsFixedFormat(0, (Join-Path $repo 'artifacts\Excel_Overview.pdf'))
    $book.Worksheets.Item('Club Pivot').ExportAsFixedFormat(0, (Join-Path $repo 'artifacts\Excel_Pivot.pdf'))
    @{excel_version=$excel.Version; reopened=$true; pivot_tables=1; pivot_value_checks=$pivotChecks.Count;
      formula_checks=$checks; pivot_checks=$pivotChecks; focus_formula_checks=4; season_change_checked=$true;
      template_opened_read_only=$true; grand_totals_suppressed=$true; pivot_captions=$captions;
      pivot_column_width=18} | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 (Join-Path $repo 'artifacts\excel_verification.json')
    Write-Output "PASS: Excel $($excel.Version); saved/reopened; 1 native PivotTable; $($pivotChecks.Count) pivot values; formulas and focus change verified"
} finally {
    if ($null -ne $book) { $book.Close($false) }
    $excel.Quit()
    [void][Runtime.InteropServices.Marshal]::ReleaseComObject($excel)
}
