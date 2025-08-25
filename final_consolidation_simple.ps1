# Final Ultimate Consolidation Script
Write-Host "🦉 FINAL ULTIMATE CONSOLIDATION STARTING..." -ForegroundColor Cyan

$startTime = Get-Date
$totalFilesProcessed = 0
$errors = 0

# Define consolidation targets
$targets = @(
    @{ name = "package.json"; pattern = "package.json"; output = "package_consolidated.json" },
    @{ name = "tsconfig"; pattern = "tsconfig*.json"; output = "tsconfig_consolidated.json" },
    @{ name = "eslint"; pattern = ".eslintrc*"; output = "eslintrc_consolidated.json" },
    @{ name = "prettier"; pattern = ".prettier*"; output = "prettier_consolidated.json" },
    @{ name = "env"; pattern = ".env*"; output = "env_consolidated.txt" },
    @{ name = "README"; pattern = "README*"; output = "README_consolidated.md" }
)

foreach ($target in $targets) {
    Write-Host "📁 Processing $($target.name)..." -ForegroundColor Green
    
    $foundFiles = Get-ChildItem -Path "." -Recurse -Name $target.pattern -ErrorAction SilentlyContinue
    
    if ($foundFiles.Count -gt 0) {
        Write-Host "   Found $($foundFiles.Count) files" -ForegroundColor Cyan
        
        $content = @()
        $content += "# ========================================================================"
        $content += "# 🦉 SPARKLING-OWL-SPIN - $($target.name.ToUpper()) CONSOLIDATION"
        $content += "# ========================================================================"
        $content += ""
        
        foreach ($file in $foundFiles) {
            try {
                $content += "# From: $file"
                $content += "# ========================================================================"
                $fileContent = Get-Content -Path $file -Raw -ErrorAction SilentlyContinue
                if ($fileContent) {
                    $content += $fileContent
                }
                $content += ""
                $totalFilesProcessed++
            }
            catch {
                Write-Host "   ⚠️  Error: $_" -ForegroundColor Yellow
                $errors++
            }
        }
        
        try {
            $content | Out-File -FilePath $target.output -Encoding UTF8
            Write-Host "   ✅ Created $($target.output)" -ForegroundColor Green
        }
        catch {
            Write-Host "   ❌ Failed to create output file" -ForegroundColor Red
            $errors++
        }
    }
    else {
        Write-Host "   ℹ️  No files found" -ForegroundColor Gray
    }
}

$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host ""
Write-Host "🎯 FINAL CONSOLIDATION COMPLETE!" -ForegroundColor Green
Write-Host "📊 Files processed: $totalFilesProcessed" -ForegroundColor Cyan
Write-Host "⚠️  Errors: $errors" -ForegroundColor $(if($errors -gt 0) { 'Red' } else { 'Green' })
Write-Host "⏱️  Duration: $($duration.TotalSeconds.ToString('F2')) seconds" -ForegroundColor Cyan

if ($errors -eq 0) {
    Write-Host "🏆 LEGENDARY CONSOLIDATION ACHIEVED!" -ForegroundColor Green
}

Write-Host "🦉 SPARKLING-OWL-SPIN: ULTIMATE CONSOLIDATION COMPLETE! ✨" -ForegroundColor Magenta
