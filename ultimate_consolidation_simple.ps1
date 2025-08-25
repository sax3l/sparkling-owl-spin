# Ultimate Configuration Consolidation Script
Write-Host "Starting Ultimate Configuration Consolidation..." -ForegroundColor Cyan

$consolidatedFiles = @{}

# 1. REQUIREMENTS FILES
Write-Host "`n1. Processing Requirements Files..." -ForegroundColor Yellow
$reqFiles = Get-ChildItem -Path "." -Recurse -Name "*requirements*.txt" -File -ErrorAction SilentlyContinue |
    Where-Object { $_ -notlike "*node_modules*" -and $_ -ne "requirements.txt" }

if ($reqFiles.Count -gt 0) {
    Write-Host "  Found $($reqFiles.Count) requirements files" -ForegroundColor Green
    
    $reqContent = @"
# 
# ████████████████████████████████████████████████████████████████████████████████████████
# ██                                                                                    ██
# ██   🦉 SPARKLING-OWL-SPIN - EXTENDED REQUIREMENTS CONSOLIDATION                    ██
# ██   All remaining requirements files from the entire project                        ██
# ██                                                                                    ██
# ████████████████████████████████████████████████████████████████████████████████████████
#

# Extended Requirements Consolidation
# Total files: $($reqFiles.Count)
# Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

"@

    foreach ($file in $reqFiles) {
        try {
            $fullPath = Get-Item $file -ErrorAction SilentlyContinue
            if ($fullPath) {
                $relativePath = $fullPath.FullName.Replace((Get-Location).Path, "").TrimStart('\')
                $reqContent += "`n# FROM: $relativePath`n"
                
                $content = Get-Content -Path $fullPath.FullName -Raw -ErrorAction SilentlyContinue
                if ($content) {
                    $reqContent += $content.TrimEnd() + "`n"
                } else {
                    $reqContent += "# (empty file)`n"
                }
                Write-Host "    Added: $relativePath" -ForegroundColor DarkGreen
            }
        }
        catch {
            Write-Host "    Failed: $file - $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    $reqContent += "`n# END OF EXTENDED REQUIREMENTS - $($reqFiles.Count) files processed`n"
    $reqContent | Out-File -FilePath "requirements_extended.txt" -Encoding UTF8
    $consolidatedFiles["requirements"] = @{ file = "requirements_extended.txt"; count = $reqFiles.Count }
    Write-Host "  Saved: requirements_extended.txt" -ForegroundColor Cyan
}

# 2. PYPROJECT FILES  
Write-Host "`n2. Processing PyProject Files..." -ForegroundColor Yellow
$pyprojectFiles = Get-ChildItem -Path "." -Recurse -Name "pyproject.toml" -File -ErrorAction SilentlyContinue |
    Where-Object { $_ -ne "pyproject.toml" }

if ($pyprojectFiles.Count -gt 0) {
    Write-Host "  Found $($pyprojectFiles.Count) pyproject.toml files" -ForegroundColor Green
    
    $pyprojectContent = @"
# 
# ████████████████████████████████████████████████████████████████████████████████████████
# ██                                                                                    ██
# ██   🦉 SPARKLING-OWL-SPIN - CONSOLIDATED PYPROJECT FILES                           ██
# ██   All pyproject.toml files from vendors and subdirectories                       ██
# ██                                                                                    ██
# ████████████████████████████████████████████████████████████████████████████████████████
#

# PyProject.toml Consolidation
# Total files: $($pyprojectFiles.Count)
# Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

"@

    foreach ($file in $pyprojectFiles) {
        try {
            $fullPath = Get-Item $file -ErrorAction SilentlyContinue
            if ($fullPath) {
                $relativePath = $fullPath.FullName.Replace((Get-Location).Path, "").TrimStart('\')
                $pyprojectContent += "`n# ===== FROM: $relativePath =====`n"
                
                $content = Get-Content -Path $fullPath.FullName -Raw -ErrorAction SilentlyContinue
                if ($content) {
                    $pyprojectContent += $content.TrimEnd() + "`n"
                } else {
                    $pyprojectContent += "# (empty file)`n"
                }
                Write-Host "    Added: $relativePath" -ForegroundColor DarkGreen
            }
        }
        catch {
            Write-Host "    Failed: $file - $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    $pyprojectContent += "`n# END OF PYPROJECT CONSOLIDATION - $($pyprojectFiles.Count) files processed`n"
    $pyprojectContent | Out-File -FilePath "pyproject_consolidated.toml" -Encoding UTF8
    $consolidatedFiles["pyproject"] = @{ file = "pyproject_consolidated.toml"; count = $pyprojectFiles.Count }
    Write-Host "  Saved: pyproject_consolidated.toml" -ForegroundColor Cyan
}

# 3. DOCKERFILE FILES
Write-Host "`n3. Processing Dockerfile Files..." -ForegroundColor Yellow
$dockerFiles = Get-ChildItem -Path "." -Recurse -Name "Dockerfile*" -File -ErrorAction SilentlyContinue

if ($dockerFiles.Count -gt 0) {
    Write-Host "  Found $($dockerFiles.Count) Dockerfile files" -ForegroundColor Green
    
    $dockerContent = @"
# 
# ████████████████████████████████████████████████████████████████████████████████████████
# ██                                                                                    ██
# ██   🦉 SPARKLING-OWL-SPIN - CONSOLIDATED DOCKERFILE COLLECTION                     ██
# ██   All Dockerfile configurations from the entire project                          ██
# ██                                                                                    ██
# ████████████████████████████████████████████████████████████████████████████████████████
#

# Dockerfile Consolidation  
# Total files: $($dockerFiles.Count)
# Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
# Note: This is a reference collection - individual Dockerfiles should be used for builds

"@

    foreach ($file in $dockerFiles) {
        try {
            $fullPath = Get-Item $file -ErrorAction SilentlyContinue
            if ($fullPath) {
                $relativePath = $fullPath.FullName.Replace((Get-Location).Path, "").TrimStart('\')
                $dockerContent += "`n# ===== FROM: $relativePath =====`n"
                
                $content = Get-Content -Path $fullPath.FullName -Raw -ErrorAction SilentlyContinue
                if ($content) {
                    $dockerContent += $content.TrimEnd() + "`n"
                } else {
                    $dockerContent += "# (empty file)`n"
                }
                Write-Host "    Added: $relativePath" -ForegroundColor DarkGreen
            }
        }
        catch {
            Write-Host "    Failed: $file - $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    $dockerContent += "`n# END OF DOCKERFILE CONSOLIDATION - $($dockerFiles.Count) files processed`n"
    $dockerContent | Out-File -FilePath "Dockerfile_consolidated" -Encoding UTF8
    $consolidatedFiles["dockerfile"] = @{ file = "Dockerfile_consolidated"; count = $dockerFiles.Count }
    Write-Host "  Saved: Dockerfile_consolidated" -ForegroundColor Cyan
}

# 4. DOCKER-COMPOSE FILES
Write-Host "`n4. Processing Docker-Compose Files..." -ForegroundColor Yellow
$composeFiles = Get-ChildItem -Path "." -Recurse -Name "docker-compose*.yml" -File -ErrorAction SilentlyContinue |
    Where-Object { $_ -notlike "*docker-compose.yml" -and $_ -notlike "*docker-compose.backend.yml" }

if ($composeFiles.Count -gt 0) {
    Write-Host "  Found $($composeFiles.Count) docker-compose files" -ForegroundColor Green
    
    $composeContent = @"
# 
# ████████████████████████████████████████████████████████████████████████████████████████
# ██                                                                                    ██
# ██   🦉 SPARKLING-OWL-SPIN - CONSOLIDATED DOCKER-COMPOSE FILES                      ██
# ██   All docker-compose configurations from the project                             ██
# ██                                                                                    ██
# ████████████████████████████████████████████████████████████████████████████████████████
#

# Docker-Compose Consolidation
# Total files: $($composeFiles.Count)  
# Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

"@

    foreach ($file in $composeFiles) {
        try {
            $fullPath = Get-Item $file -ErrorAction SilentlyContinue
            if ($fullPath) {
                $relativePath = $fullPath.FullName.Replace((Get-Location).Path, "").TrimStart('\')
                $composeContent += "`n# ===== FROM: $relativePath =====`n"
                
                $content = Get-Content -Path $fullPath.FullName -Raw -ErrorAction SilentlyContinue
                if ($content) {
                    $composeContent += $content.TrimEnd() + "`n"
                } else {
                    $composeContent += "# (empty file)`n"
                }
                Write-Host "    Added: $relativePath" -ForegroundColor DarkGreen
            }
        }
        catch {
            Write-Host "    Failed: $file - $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    $composeContent += "`n# END OF DOCKER-COMPOSE CONSOLIDATION - $($composeFiles.Count) files processed`n"
    $composeContent | Out-File -FilePath "docker-compose_consolidated.yml" -Encoding UTF8
    $consolidatedFiles["compose"] = @{ file = "docker-compose_consolidated.yml"; count = $composeFiles.Count }
    Write-Host "  Saved: docker-compose_consolidated.yml" -ForegroundColor Cyan
}

# 5. MAKEFILE FILES
Write-Host "`n5. Processing Makefile Files..." -ForegroundColor Yellow
$makeFiles = Get-ChildItem -Path "." -Recurse -Name "Makefile*" -File -ErrorAction SilentlyContinue |
    Where-Object { $_ -ne "Makefile" -and $_ -ne "Makefile.sos" -and $_ -ne "Makefile.tests" }

if ($makeFiles.Count -gt 0) {
    Write-Host "  Found $($makeFiles.Count) additional Makefile files" -ForegroundColor Green
    
    $makeContent = @"
# 
# ████████████████████████████████████████████████████████████████████████████████████████
# ██                                                                                    ██
# ██   🦉 SPARKLING-OWL-SPIN - CONSOLIDATED MAKEFILE COLLECTION                       ██
# ██   All Makefile configurations from vendors and subdirectories                    ██
# ██                                                                                    ██
# ████████████████████████████████████████████████████████████████████████████████████████
#

# Makefile Consolidation
# Total files: $($makeFiles.Count)
# Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

"@

    foreach ($file in $makeFiles) {
        try {
            $fullPath = Get-Item $file -ErrorAction SilentlyContinue
            if ($fullPath) {
                $relativePath = $fullPath.FullName.Replace((Get-Location).Path, "").TrimStart('\')
                $makeContent += "`n# ===== FROM: $relativePath =====`n"
                
                $content = Get-Content -Path $fullPath.FullName -Raw -ErrorAction SilentlyContinue
                if ($content) {
                    $makeContent += $content.TrimEnd() + "`n"
                } else {
                    $makeContent += "# (empty file)`n"
                }
                Write-Host "    Added: $relativePath" -ForegroundColor DarkGreen
            }
        }
        catch {
            Write-Host "    Failed: $file - $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    $makeContent += "`n# END OF MAKEFILE CONSOLIDATION - $($makeFiles.Count) files processed`n"
    $makeContent | Out-File -FilePath "Makefile_consolidated" -Encoding UTF8
    $consolidatedFiles["makefile"] = @{ file = "Makefile_consolidated"; count = $makeFiles.Count }
    Write-Host "  Saved: Makefile_consolidated" -ForegroundColor Cyan
}

# Create summary report
$totalFiles = ($consolidatedFiles.Values | Measure-Object -Property count -Sum).Sum

$reportContent = @"
# 
# ████████████████████████████████████████████████████████████████████████████████████████
# ██                                                                                    ██
# ██   🦉 SPARKLING-OWL-SPIN - ULTIMATE CONSOLIDATION REPORT                          ██
# ██   Complete configuration file consolidation summary                               ██
# ██                                                                                    ██
# ████████████████████████████████████████████████████████████████████████████████████████
#

# ULTIMATE CONSOLIDATION SUMMARY
- **Total configuration files processed**: $totalFiles
- **Consolidation types**: $($consolidatedFiles.Count)
- **Generated**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

## 📁 CONSOLIDATED FILES CREATED

"@

foreach ($consolidated in $consolidatedFiles.GetEnumerator()) {
    $info = $consolidated.Value
    $reportContent += "### $($consolidated.Key.ToUpper())`n"
    $reportContent += "- **File**: ``$($info.file)```n"
    $reportContent += "- **Sources**: $($info.count) files`n`n"
}

$reportContent += @"
## ✨ BENEFITS ACHIEVED
- **Centralized configuration** - All config types in dedicated consolidated files
- **Easy comparison** - See all variations of each config type in one place
- **Project overview** - Complete picture of all configurations used
- **Maintenance efficiency** - Single files to review for each configuration type
- **Documentation** - Self-documenting consolidated files with source paths

## 🎯 FILES LOCATION
All consolidated files are now in the project root:

"@

foreach ($consolidated in $consolidatedFiles.GetEnumerator()) {
    $reportContent += "- ``$($consolidated.Value.file)`` ($($consolidated.Value.count) sources)`n"
}

$reportContent += @"

---
**Status**: ✅ ULTIMATE CONSOLIDATION COMPLETE  
**Total Sources**: $totalFiles files → $($consolidatedFiles.Count) consolidated files
**Project**: Sparkling-Owl-Spin v1.0.0
"@

$reportContent | Out-File -FilePath "ULTIMATE_CONSOLIDATION_REPORT.md" -Encoding UTF8

Write-Host "`nULTIMATE CONSOLIDATION COMPLETE!" -ForegroundColor Cyan
Write-Host "Total files processed: $totalFiles" -ForegroundColor Yellow
Write-Host "Consolidated files created: $($consolidatedFiles.Count)" -ForegroundColor Yellow
Write-Host "Report saved: ULTIMATE_CONSOLIDATION_REPORT.md" -ForegroundColor Yellow

Write-Host "`nFILES CREATED:" -ForegroundColor Cyan
foreach ($consolidated in $consolidatedFiles.GetEnumerator()) {
    Write-Host "  $($consolidated.Value.file) ($($consolidated.Value.count) sources)" -ForegroundColor Green
}

Write-Host "`nUltimate consolidation completed successfully!" -ForegroundColor Green
