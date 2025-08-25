# Cleanup Script for Consolidated Configuration Files
Write-Host "Starting cleanup of original configuration files..." -ForegroundColor Cyan

$removedFiles = 0
$errorCount = 0
$fileTypes = @{}

# 1. REMOVE EXTENDED REQUIREMENTS FILES
Write-Host "`n1. Removing extended requirements files..." -ForegroundColor Yellow
$reqFiles = Get-ChildItem -Path "." -Recurse -Name "*requirements*.txt" -File -ErrorAction SilentlyContinue |
    Where-Object { $_ -notlike "*node_modules*" -and $_ -ne "requirements.txt" -and $_ -ne "requirements_extended.txt" }

foreach ($file in $reqFiles) {
    try {
        $fullPath = Get-Item $file -ErrorAction SilentlyContinue
        if ($fullPath -and (Test-Path $fullPath.FullName)) {
            Remove-Item -Path $fullPath.FullName -Force
            Write-Host "  Removed: $file" -ForegroundColor DarkGreen
            $removedFiles++
        }
    }
    catch {
        Write-Host "  Failed: $file - $($_.Exception.Message)" -ForegroundColor Red
        $errorCount++
    }
}
$fileTypes["requirements"] = $reqFiles.Count

# 2. REMOVE PYPROJECT FILES (keeping main one)
Write-Host "`n2. Removing pyproject.toml files..." -ForegroundColor Yellow
$pyprojectFiles = Get-ChildItem -Path "." -Recurse -Name "pyproject.toml" -File -ErrorAction SilentlyContinue |
    Where-Object { $_ -ne "pyproject.toml" }

foreach ($file in $pyprojectFiles) {
    try {
        $fullPath = Get-Item $file -ErrorAction SilentlyContinue
        if ($fullPath -and (Test-Path $fullPath.FullName)) {
            Remove-Item -Path $fullPath.FullName -Force
            Write-Host "  Removed: $($fullPath.FullName.Replace((Get-Location).Path, '').TrimStart('\'))" -ForegroundColor DarkGreen
            $removedFiles++
        }
    }
    catch {
        Write-Host "  Failed: $file - $($_.Exception.Message)" -ForegroundColor Red
        $errorCount++
    }
}
$fileTypes["pyproject"] = $pyprojectFiles.Count

# 3. REMOVE DOCKERFILE FILES (keeping main ones)
Write-Host "`n3. Removing Dockerfile files..." -ForegroundColor Yellow
$dockerFiles = Get-ChildItem -Path "." -Recurse -Name "Dockerfile*" -File -ErrorAction SilentlyContinue |
    Where-Object { 
        $_ -notlike "*backend\Dockerfile*" -and 
        $_ -notlike "*docker\Dockerfile*" -and 
        $_ -ne "Dockerfile_consolidated"
    }

$dockerRemoved = 0
foreach ($file in $dockerFiles) {
    try {
        $fullPath = Get-Item $file -ErrorAction SilentlyContinue
        if ($fullPath -and (Test-Path $fullPath.FullName)) {
            Remove-Item -Path $fullPath.FullName -Force
            $dockerRemoved++
            if ($dockerRemoved % 20 -eq 0) {
                Write-Host "  Removed: $dockerRemoved Dockerfile files..." -ForegroundColor DarkGreen
            }
            $removedFiles++
        }
    }
    catch {
        Write-Host "  Failed: $file - $($_.Exception.Message)" -ForegroundColor Red
        $errorCount++
    }
}
Write-Host "  Total Dockerfiles removed: $dockerRemoved" -ForegroundColor Green
$fileTypes["dockerfile"] = $dockerFiles.Count

# 4. REMOVE DOCKER-COMPOSE FILES (keeping main ones)
Write-Host "`n4. Removing docker-compose files..." -ForegroundColor Yellow
$composeFiles = Get-ChildItem -Path "." -Recurse -Name "docker-compose*.yml" -File -ErrorAction SilentlyContinue |
    Where-Object { 
        $_ -notlike "*docker-compose.yml*" -and 
        $_ -notlike "*docker-compose.backend.yml*" -and 
        $_ -ne "docker-compose_consolidated.yml"
    }

foreach ($file in $composeFiles) {
    try {
        $fullPath = Get-Item $file -ErrorAction SilentlyContinue
        if ($fullPath -and (Test-Path $fullPath.FullName)) {
            Remove-Item -Path $fullPath.FullName -Force
            Write-Host "  Removed: $($fullPath.FullName.Replace((Get-Location).Path, '').TrimStart('\'))" -ForegroundColor DarkGreen
            $removedFiles++
        }
    }
    catch {
        Write-Host "  Failed: $file - $($_.Exception.Message)" -ForegroundColor Red
        $errorCount++
    }
}
$fileTypes["compose"] = $composeFiles.Count

# 5. REMOVE MAKEFILE FILES (keeping main ones)
Write-Host "`n5. Removing additional Makefile files..." -ForegroundColor Yellow
$makeFiles = Get-ChildItem -Path "." -Recurse -Name "Makefile*" -File -ErrorAction SilentlyContinue |
    Where-Object { 
        $_ -ne "Makefile" -and 
        $_ -ne "Makefile.sos" -and 
        $_ -ne "Makefile.tests" -and 
        $_ -ne "Makefile_consolidated"
    }

$makeRemoved = 0
foreach ($file in $makeFiles) {
    try {
        $fullPath = Get-Item $file -ErrorAction SilentlyContinue
        if ($fullPath -and (Test-Path $fullPath.FullName)) {
            Remove-Item -Path $fullPath.FullName -Force
            $makeRemoved++
            if ($makeRemoved % 10 -eq 0) {
                Write-Host "  Removed: $makeRemoved Makefile files..." -ForegroundColor DarkGreen
            }
            $removedFiles++
        }
    }
    catch {
        Write-Host "  Failed: $file - $($_.Exception.Message)" -ForegroundColor Red
        $errorCount++
    }
}
Write-Host "  Total Makefiles removed: $makeRemoved" -ForegroundColor Green
$fileTypes["makefile"] = $makeFiles.Count

# Remove the consolidation scripts
Write-Host "`n6. Removing consolidation scripts..." -ForegroundColor Yellow
$scriptsToRemove = @(
    "ultimate_consolidation.ps1", 
    "ultimate_consolidation_simple.ps1"
)

foreach ($script in $scriptsToRemove) {
    if (Test-Path $script) {
        try {
            Remove-Item -Path $script -Force
            Write-Host "  Removed: $script" -ForegroundColor DarkGreen
            $removedFiles++
        }
        catch {
            Write-Host "  Failed: $script - $($_.Exception.Message)" -ForegroundColor Red
            $errorCount++
        }
    }
}

# Create cleanup report
$reportContent = @"
# 
# ████████████████████████████████████████████████████████████████████████████████████████
# ██                                                                                    ██
# ██   🦉 SPARKLING-OWL-SPIN - CONFIGURATION CLEANUP REPORT                           ██
# ██   Summary of all configuration files removed after consolidation                 ██
# ██                                                                                    ██
# ████████████████████████████████████████████████████████████████████████████████████████
#

# CLEANUP SUMMARY
- **Total files removed**: $removedFiles
- **Errors encountered**: $errorCount
- **Generated**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

## 📁 FILES REMOVED BY TYPE

"@

foreach ($fileType in $fileTypes.GetEnumerator()) {
    $reportContent += "### $($fileType.Key.ToUpper())`n"
    $reportContent += "- **Files removed**: $($fileType.Value)`n`n"
}

$reportContent += @"
## ✅ REMAINING CONSOLIDATED FILES
The following consolidated files remain in the project root:

- ``requirements.txt`` - Original consolidated requirements
- ``requirements_extended.txt`` - Extended requirements from engines/vendors
- ``pyproject.toml`` - Main project configuration  
- ``pyproject_consolidated.toml`` - All vendor pyproject files
- ``Dockerfile_consolidated`` - All Dockerfile configurations
- ``docker-compose_consolidated.yml`` - All compose configurations
- ``Makefile_consolidated`` - All Makefile configurations
- ``.github/`` - Consolidated GitHub configurations
- ``.gitignore`` - Consolidated ignore patterns

## 🎯 BENEFITS ACHIEVED
- **Single source of truth** for each configuration type
- **Dramatically reduced file count** - $removedFiles files removed
- **Easy maintenance** with centralized configuration files
- **Clean project structure** with consolidated configs
- **Complete historical reference** in consolidated files

---
**Status**: ✅ CONFIGURATION CLEANUP COMPLETE
**Files Removed**: $removedFiles
**Consolidated Files**: 9 configuration files remain
**Project**: Sparkling-Owl-Spin v1.0.0
"@

$reportContent | Out-File -FilePath "CONFIGURATION_CLEANUP_REPORT.md" -Encoding UTF8

Write-Host "`nCONFIGURATION CLEANUP COMPLETE!" -ForegroundColor Cyan
Write-Host "Total files removed: $removedFiles" -ForegroundColor Yellow
Write-Host "Errors: $errorCount" -ForegroundColor $(if ($errorCount -gt 0) { 'Red' } else { 'Green' })
Write-Host "Report saved: CONFIGURATION_CLEANUP_REPORT.md" -ForegroundColor Yellow

Write-Host "`nFILES REMOVED BY TYPE:" -ForegroundColor Cyan
foreach ($fileType in $fileTypes.GetEnumerator()) {
    Write-Host "  $($fileType.Key): $($fileType.Value) files" -ForegroundColor Green
}

if ($errorCount -eq 0) {
    Write-Host "`nAll configuration cleanup completed successfully!" -ForegroundColor Green
} else {
    Write-Host "`nCleanup completed with $errorCount errors. Check the log above." -ForegroundColor Yellow
}
