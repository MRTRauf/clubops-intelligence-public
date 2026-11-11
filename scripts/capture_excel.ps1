$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class ClubOpsWindow {
 [StructLayout(LayoutKind.Sequential)] public struct RECT {public int Left,Top,Right,Bottom;}
 [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hwnd, out RECT rect);
 [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hwnd, IntPtr dc, uint flags);
}
'@
$repo = Split-Path -Parent $PSScriptRoot
$excel = New-Object -ComObject Excel.Application
$book = $null
try {
    $excel.DisplayAlerts = $false
    $book = $excel.Workbooks.Open((Join-Path $repo 'artifacts\ClubOps_Reporting_COMPLETED.xlsx'),0,$true)
    $excel.Visible = $true
    $excel.WindowState = -4137
    foreach ($sheet in @('Overview','Club Pivot')) {
        $book.Worksheets.Item($sheet).Activate()
        $excel.ActiveWindow.Zoom = 70
        Start-Sleep -Milliseconds 800
        $rect = New-Object ClubOpsWindow+RECT
        [void][ClubOpsWindow]::GetWindowRect([IntPtr]$excel.Hwnd,[ref]$rect)
        $bitmap = New-Object Drawing.Bitmap ($rect.Right-$rect.Left),($rect.Bottom-$rect.Top)
        $graphics = [Drawing.Graphics]::FromImage($bitmap)
        $dc = $graphics.GetHdc()
        try { $ok = [ClubOpsWindow]::PrintWindow([IntPtr]$excel.Hwnd,$dc,2) } finally { $graphics.ReleaseHdc($dc) }
        if (-not $ok) { throw 'Excel window capture failed' }
        $target = Join-Path $repo ('artifacts\screenshots\Excel_'+$sheet.Replace(' ','_')+'.png')
        $bitmap.Save($target,[Drawing.Imaging.ImageFormat]::Png)
        $graphics.Dispose()
        $bitmap.Dispose()
        Write-Output "Captured actual Excel window: $target"
    }
} finally {
    if ($null -ne $book) { $book.Close($false) }
    $excel.Quit()
    [void][Runtime.InteropServices.Marshal]::ReleaseComObject($excel)
}
