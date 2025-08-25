# PowerShell script to remove all old requirements files
# Keeps only the main requirements.txt in root

Write-Host "🗑️ Removing all old requirements files..." -ForegroundColor Red

# Get all requirements files except the main one
$filesToRemove = Get-ChildItem -Path "." -Recurse -Name "requirements*.txt" | 
    Where-Object { 
        $_ -ne "requirements.txt" -and 
        $_ -ne ".\requirements.txt" -and 
        (Split-Path $_) -ne "." 
    }

Write-Host "Found $($filesToRemove.Count) requirements files to remove:" -ForegroundColor Yellow

$removedCount = 0
$failedCount = 0

foreach ($file in $filesToRemove) {
    try {
        if (Test-Path $file) {
            Write-Host "  Removing: $file" -ForegroundColor Gray
            Remove-Item $file -Force
            $removedCount++
        }
    }
    catch {
        Write-Host "  Failed to remove: $file - $($_.Exception.Message)" -ForegroundColor Red
        $failedCount++
    }
}

Write-Host ""
Write-Host "✅ Cleanup complete!" -ForegroundColor Green
Write-Host "📊 Summary:" -ForegroundColor Yellow
Write-Host "  Files removed: $removedCount" -ForegroundColor White
Write-Host "  Files failed: $failedCount" -ForegroundColor White
Write-Host "  Remaining: requirements.txt (main file)" -ForegroundColor Green
