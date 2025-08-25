# 
# ████████████████████████████████████████████████████████████████████████████████████████
# ██                                                                                    ██
# ██   🦉 SPARKLING-OWL-SPIN - FINAL ULTIMATE CONSOLIDATION                           ██
# ██   One last comprehensive consolidation of ALL remaining files                     ██
# ██                                                                                    ██
# ████████████████████████████████████████████████████████████████████████████████████████
#

Write-Host "🦉 FINAL ULTIMATE CONSOLIDATION STARTING..." -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Yellow

$startTime = Get-Date
$totalFilesProcessed = 0
$totalFilesRemoved = 0
$errors = 0

# Final consolidation targets
$consolidationTargets = @{
    "package.json" = @{
        "pattern" = "package.json"
        "output" = "package_consolidated.json"
        "description" = "All Node.js package configurations"
    }
    "tsconfig.json" = @{
        "pattern" = "tsconfig*.json"
        "output" = "tsconfig_consolidated.json"
        "description" = "All TypeScript configurations"
    }
    "eslint" = @{
        "pattern" = ".eslintrc*"
        "output" = "eslintrc_consolidated.json"
        "description" = "All ESLint configurations"
    }
    "prettier" = @{
        "pattern" = ".prettier*"
        "output" = "prettier_consolidated.json"
        "description" = "All Prettier configurations"
    }
    "babel" = @{
        "pattern" = ".babelrc*", "babel.config.*"
        "output" = "babel_consolidated.json"
        "description" = "All Babel configurations"
    }
    "webpack" = @{
        "pattern" = "webpack*.js", "webpack*.config.js"
        "output" = "webpack_consolidated.js"
        "description" = "All Webpack configurations"
    }
    "rollup" = @{
        "pattern" = "rollup*.js", "rollup*.config.js"
        "output" = "rollup_consolidated.js"
        "description" = "All Rollup configurations"
    }
    "vite" = @{
        "pattern" = "vite*.js", "vite*.config.js", "vite*.config.ts"
        "output" = "vite_consolidated.js"
        "description" = "All Vite configurations"
    }
    "jest" = @{
        "pattern" = "jest*.js", "jest*.config.js", "jest.config.json"
        "output" = "jest_consolidated.js"
        "description" = "All Jest configurations"
    }
    "cypress" = @{
        "pattern" = "cypress*.js", "cypress*.config.js", "cypress.json"
        "output" = "cypress_consolidated.js"
        "description" = "All Cypress configurations"
    }
    "env" = @{
        "pattern" = ".env*"
        "output" = "env_consolidated.txt"
        "description" = "All environment configurations"
    }
    "editorconfig" = @{
        "pattern" = ".editorconfig"
        "output" = "editorconfig_consolidated.txt"
        "description" = "All editor configurations"
    }
    "LICENSE" = @{
        "pattern" = "LICENSE*", "LICENCE*"
        "output" = "LICENSE_consolidated.txt"
        "description" = "All license files"
    }
    "README" = @{
        "pattern" = "README*"
        "output" = "README_consolidated.md"
        "description" = "All README files"
    }
}

Write-Host "🔍 Searching for files to consolidate..." -ForegroundColor Yellow

foreach ($type in $consolidationTargets.Keys) {
    $config = $consolidationTargets[$type]
    $patterns = $config.pattern
    $outputFile = $config.output
    $description = $config.description
    
    Write-Host "📁 Processing $description..." -ForegroundColor Green
    
    $foundFiles = @()
    
    # Handle multiple patterns
    if ($patterns -is [array]) {
        foreach ($pattern in $patterns) {
            $files = Get-ChildItem -Path "." -Recurse -Name $pattern -ErrorAction SilentlyContinue
            $foundFiles += $files
        }
    } else {
        $foundFiles = Get-ChildItem -Path "." -Recurse -Name $patterns -ErrorAction SilentlyContinue
    }
    
    if ($foundFiles.Count -gt 0) {
        Write-Host "   Found $($foundFiles.Count) files for $type" -ForegroundColor Cyan
        
        # Create consolidated file
        $consolidatedContent = @()
        $consolidatedContent += "#"
        $consolidatedContent += "# ████████████████████████████████████████████████████████████████████████████████████████"
        $consolidatedContent += "# ██                                                                                    ██"
        $consolidatedContent += "# ██   🦉 SPARKLING-OWL-SPIN - $($description.ToUpper().PadRight(49)) ██"
        $consolidatedContent += "# ██   Final consolidation of all $type files$((' ' * (47 - $type.Length))) ██"
        $consolidatedContent += "# ██                                                                                    ██"
        $consolidatedContent += "# ████████████████████████████████████████████████████████████████████████████████████████"
        $consolidatedContent += "#"
        $consolidatedContent += ""
        
        foreach ($file in $foundFiles) {
            try {
                $fullPath = Resolve-Path $file -ErrorAction SilentlyContinue
                if ($fullPath) {
                    $consolidatedContent += "# ========================================================================"
                    $consolidatedContent += "# From: $file"
                    $consolidatedContent += "# ========================================================================"
                    $consolidatedContent += ""
                    
                    $content = Get-Content -Path $fullPath -Raw -ErrorAction SilentlyContinue
                    if ($content) {
                        $consolidatedContent += $content
                    } else {
                        $consolidatedContent += "# [Empty or unreadable file]"
                    }
                    $consolidatedContent += ""
                    $totalFilesProcessed++
                }
            }
            catch {
                Write-Host "   ⚠️  Error reading $file`: $_" -ForegroundColor Yellow
                $errors++
            }
        }
        
        # Save consolidated file
        try {
            $consolidatedContent | Out-File -FilePath $outputFile -Encoding UTF8
            Write-Host "   ✅ Created $outputFile with $($foundFiles.Count) sources" -ForegroundColor Green
        }
        catch {
            Write-Host "   ❌ Failed to create $outputFile`: $_" -ForegroundColor Red
            $errors++
        }
    } else {
        Write-Host "   ℹ️  No $type files found" -ForegroundColor Gray
    }
}

# Final summary
$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host ""
Write-Host "🎯 FINAL ULTIMATE CONSOLIDATION COMPLETE!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Yellow
Write-Host "📊 Files processed: $totalFilesProcessed" -ForegroundColor Cyan
Write-Host "⚠️  Errors: $errors" -ForegroundColor $(if($errors -gt 0) { 'Red' } else { 'Green' })
Write-Host "⏱️  Duration: $($duration.TotalSeconds.ToString('F2')) seconds" -ForegroundColor Cyan
Write-Host ""

if ($errors -eq 0) {
    Write-Host "🏆 LEGENDARY CONSOLIDATION STATUS ACHIEVED!" -ForegroundColor Green
    Write-Host "All remaining configuration files have been consolidated!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Consolidation completed with $errors errors" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🦉 SPARKLING-OWL-SPIN: ULTIMATE PROJECT CONSOLIDATION COMPLETE! ✨" -ForegroundColor Magenta
