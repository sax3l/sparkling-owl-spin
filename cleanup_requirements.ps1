# PowerShell script to remove all old requirements files
Write-Host "Removing old requirements files..." -ForegroundColor Red

$filesToRemove = Get-ChildItem -Path "." -Recurse -Name "requirements*.txt" | 
    Where-Object { $_ -ne "requirements.txt" -and (Split-Path $_ -Parent) -ne "." }

$removedCount = 0
foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        Write-Host "Removing: $file" -ForegroundColor Gray
        Remove-Item $file -Force
        $removedCount++
    }
}

Write-Host "Removed $removedCount files" -ForegroundColor Green
