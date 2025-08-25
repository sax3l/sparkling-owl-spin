# Final Cleanup Script - Remove Original Files After Consolidation
Write-Host "FINAL CLEANUP STARTING..." -ForegroundColor Cyan

$startTime = Get-Date
$totalFilesRemoved = 0
$errors = 0

# Files that were consolidated - now safe to remove
$filesToRemove = @(
    "package.json",
    "tsconfig*.json", 
    ".eslintrc*",
    ".prettier*",
    ".env*",
    "README*"
)

# Exclude the main consolidated files and important root files
$excludeFiles = @(
    "package_consolidated.json",
    "tsconfig_consolidated.json", 
    "eslintrc_consolidated.json",
    "prettier_consolidated.json",
    "env_consolidated.txt",
    "README_consolidated.md",
    ".\package.json",
    ".\README.md",
    ".\tsconfig.json"
)

foreach ($pattern in $filesToRemove) {
    Write-Host "Cleaning up $pattern files..." -ForegroundColor Yellow
    
    $foundFiles = Get-ChildItem -Path "." -Recurse -Name $pattern -ErrorAction SilentlyContinue
    
    foreach ($file in $foundFiles) {
        $shouldExclude = $false
        foreach ($exclude in $excludeFiles) {
            if ($file -like $exclude -or $file -eq $exclude) {
                $shouldExclude = $true
                break
            }
        }
        
        if (-not $shouldExclude -and $file -ne "package.json" -and $file -ne "README.md") {
            try {
                Remove-Item -Path $file -Force -ErrorAction Stop
                $totalFilesRemoved++
                if ($totalFilesRemoved % 100 -eq 0) {
                    Write-Host "   Removed $totalFilesRemoved files..." -ForegroundColor Gray
                }
            }
            catch {
                Write-Host "   Error removing $file`: $_" -ForegroundColor Red
                $errors++
            }
        }
    }
}

# Clean up our temporary scripts
$scriptsToRemove = @(
    "final_ultimate_consolidation.ps1",
    "final_consolidation_simple.ps1",
    "final_simple.ps1"
)

foreach ($script in $scriptsToRemove) {
    if (Test-Path $script) {
        try {
            Remove-Item -Path $script -Force
            Write-Host "Removed script: $script" -ForegroundColor Gray
        }
        catch {
            Write-Host "Error removing script $script`: $_" -ForegroundColor Red
        }
    }
}

$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host ""
Write-Host "FINAL CLEANUP COMPLETE!" -ForegroundColor Green
Write-Host "Files removed: $totalFilesRemoved" -ForegroundColor Cyan
Write-Host "Errors: $errors" -ForegroundColor $(if($errors -gt 0) { 'Red' } else { 'Green' })
Write-Host "Duration: $($duration.TotalSeconds.ToString('F2')) seconds" -ForegroundColor Cyan

if ($errors -eq 0) {
    Write-Host "PERFECT CLEANUP ACHIEVED!" -ForegroundColor Green
}

Write-Host "SPARKLING-OWL-SPIN: FINAL CLEANUP COMPLETE!" -ForegroundColor Magenta
