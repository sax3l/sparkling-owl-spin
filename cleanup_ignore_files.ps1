# PowerShell script to remove all old ignore files
# Keeps only the main .gitignore in root

Write-Host "🗑️ Removing all old ignore files..." -ForegroundColor Red

# Get all ignore files except the main .gitignore
$gitignoreFiles = Get-ChildItem -Path "." -Recurse -Name ".gitignore" | 
    Where-Object { (Split-Path $_ -Parent) -ne "." }

$dockerignoreFiles = Get-ChildItem -Path "." -Recurse -Name ".dockerignore"
$prettierignoreFiles = Get-ChildItem -Path "." -Recurse -Name ".prettierignore"
$otherIgnoreFiles = Get-ChildItem -Path "." -Recurse -Name "*ignore" | 
    Where-Object { $_ -notmatch "\.gitignore$" -and $_ -notmatch "\.dockerignore$" -and $_ -notmatch "\.prettierignore$" }

$allFilesToRemove = @()
$allFilesToRemove += $gitignoreFiles
$allFilesToRemove += $dockerignoreFiles
$allFilesToRemove += $prettierignoreFiles
$allFilesToRemove += $otherIgnoreFiles

Write-Host "Found $($allFilesToRemove.Count) ignore files to remove:" -ForegroundColor Yellow

$removedCount = 0
$failedCount = 0

foreach ($file in $allFilesToRemove) {
    try {
        if (Test-Path $file) {
            Write-Host "  Removing: $file" -ForegroundColor Gray
            Remove-Item $file -Force
            $removedCount++
        }
    }
    catch {
        Write-Host "  Failed to remove: $file" -ForegroundColor Red
        $failedCount++
    }
}

Write-Host ""
Write-Host "✅ Cleanup complete!" -ForegroundColor Green
Write-Host "📊 Summary:" -ForegroundColor Yellow
Write-Host "  Files removed: $removedCount" -ForegroundColor White
Write-Host "  Files failed: $failedCount" -ForegroundColor White
Write-Host "  Remaining: .gitignore (main file)" -ForegroundColor Green
