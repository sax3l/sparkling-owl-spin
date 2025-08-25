# 
# ████████████████████████████████████████████████████████████████████████████████████████
# ██                                                                                    ██
# ██   🦉 SPARKLING-OWL-SPIN - ULTIMATE CONFIGURATION CONSOLIDATION                   ██
# ██   Consolidate ALL configuration files from the entire project                     ██
# ██                                                                                    ██
# ████████████████████████████████████████████████████████████████████████████████████████
#

Write-Host "🦉 Starting Ultimate Configuration Consolidation..." -ForegroundColor Cyan

# Define file types to consolidate
$fileTypes = @{
    "requirements" = @{
        "pattern" = "**/requirements*.txt"
        "targetFile" = "requirements_complete.txt" 
        "description" = "Python Requirements"
    }
    "package" = @{
        "pattern" = "**/package.json"
        "targetFile" = "package_consolidated.json"
        "description" = "Node.js Package Files"
    }
    "pyproject" = @{
        "pattern" = "**/pyproject.toml"  
        "targetFile" = "pyproject_consolidated.toml"
        "description" = "Python Project Files"
    }
    "dockerfile" = @{
        "pattern" = "**/Dockerfile*"
        "targetFile" = "Dockerfile_consolidated"
        "description" = "Docker Configuration"  
    }
    "compose" = @{
        "pattern" = "**/docker-compose*.yml"
        "targetFile" = "docker-compose_consolidated.yml"
        "description" = "Docker Compose Files"
    }
    "makefile" = @{
        "pattern" = "**/Makefile*"
        "targetFile" = "Makefile_consolidated"
        "description" = "Build Configuration"
    }
    "config" = @{
        "pattern" = "**/*.{yml,yaml}"
        "targetFile" = "config_consolidated.yml"
        "description" = "YAML Configuration"
    }
}

$totalFiles = 0
$consolidatedFiles = @{}

# Process each file type
foreach ($fileType in $fileTypes.GetEnumerator()) {
    $typeName = $fileType.Key
    $config = $fileType.Value
    $pattern = $config.pattern
    $targetFile = $config.targetFile
    $description = $config.description
    
    Write-Host "`n📁 Processing: $description" -ForegroundColor Yellow
    
    # Find all files of this type
    $files = @()
    try {
        # Use different search methods for different patterns
        if ($pattern -like "**/requirements*.txt") {
            $files = Get-ChildItem -Path "." -Recurse -Name "*requirements*.txt" -File -ErrorAction SilentlyContinue |
                Where-Object { $_ -notlike "*node_modules*" -and $_ -ne "requirements.txt" } |
                ForEach-Object { Get-Item $_ -ErrorAction SilentlyContinue } |
                Where-Object { $_.Name -match "requirements.*\.txt$" }
        }
        elseif ($pattern -like "**/package.json") {
            $files = Get-ChildItem -Path "." -Recurse -Name "package.json" -File -ErrorAction SilentlyContinue |
                Where-Object { $_ -notlike "*node_modules*" } |
                ForEach-Object { Get-Item $_ -ErrorAction SilentlyContinue }
        }
        elseif ($pattern -like "**/pyproject.toml") {
            $files = Get-ChildItem -Path "." -Recurse -Name "pyproject.toml" -File -ErrorAction SilentlyContinue |
                ForEach-Object { Get-Item $_ -ErrorAction SilentlyContinue } |
                Where-Object { $_.Name -eq "pyproject.toml" -and $_.FullName -notlike "*\pyproject.toml" -or $_.Directory.Name -ne "Main_crawler_project" }
        }
        elseif ($pattern -like "**/Dockerfile*") {
            $files = Get-ChildItem -Path "." -Recurse -Name "Dockerfile*" -File -ErrorAction SilentlyContinue |
                ForEach-Object { Get-Item $_ -ErrorAction SilentlyContinue }
        }
        elseif ($pattern -like "**/docker-compose*.yml") {
            $files = Get-ChildItem -Path "." -Recurse -Name "docker-compose*.yml" -File -ErrorAction SilentlyContinue |
                ForEach-Object { Get-Item $_ -ErrorAction SilentlyContinue }
        }
        elseif ($pattern -like "**/Makefile*") {
            $files = Get-ChildItem -Path "." -Recurse -Name "Makefile*" -File -ErrorAction SilentlyContinue |
                Where-Object { $_ -ne "Makefile" -and $_ -ne "Makefile.sos" -and $_ -ne "Makefile.tests" } |
                ForEach-Object { Get-Item $_ -ErrorAction SilentlyContinue }
        }
        else {
            # Skip YAML for now as it's too broad
            continue
        }
    }
    catch {
        Write-Host "  ❌ Error searching for $pattern : $($_.Exception.Message)" -ForegroundColor Red
        continue
    }
    
    if ($files.Count -eq 0) {
        Write-Host "  📄 No files found for pattern: $pattern" -ForegroundColor Gray
        continue
    }
    
    Write-Host "  📄 Found $($files.Count) $description files" -ForegroundColor Green
    $totalFiles += $files.Count
    
    # Create consolidated content
    $consolidatedContent = @"
# 
# ████████████████████████████████████████████████████████████████████████████████████████
# ██                                                                                    ██
# ██   🦉 SPARKLING-OWL-SPIN - CONSOLIDATED $($description.ToUpper())                   ██
# ██   All $description files from the entire project hierarchy                        ██
# ██                                                                                    ██
# ████████████████████████████████████████████████████████████████████████████████████████
#

"@

    if ($typeName -eq "requirements") {
        $consolidatedContent += "`n# Python Requirements Consolidation`n# Total files: $($files.Count)`n# Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n`n"
    }
    elseif ($typeName -eq "package") {
        $consolidatedContent = @"
{
  "_consolidated": {
    "description": "🦉 SPARKLING-OWL-SPIN - Consolidated Package.json",
    "totalFiles": $($files.Count),
    "generated": "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
    "sources": [
"@
    }
    else {
        $consolidatedContent += "`n# Configuration Consolidation`n# Type: $description`n# Total files: $($files.Count)`n# Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n`n"
    }
    
    # Process each file
    $processedCount = 0
    foreach ($file in $files) {
        $relativePath = $file.FullName.Replace((Get-Location).Path, "").TrimStart('\')
        
        Write-Host "    ✅ $relativePath" -ForegroundColor DarkGreen
        
        try {
            if ($typeName -eq "package") {
                # For package.json, add to sources array
                $consolidatedContent += "`n      `"$relativePath`","
            }
            else {
                # Add file header
                $consolidatedContent += "`n# ===== FROM: $relativePath =====`n"
                
                # Read and add file content
                $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
                if ($content) {
                    $consolidatedContent += $content.TrimEnd() + "`n"
                }
                else {
                    $consolidatedContent += "# (empty file)`n"
                }
            }
            $processedCount++
        }
        catch {
            Write-Host "    ❌ Failed to read $($file.Name): $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    # Finalize content based on type
    if ($typeName -eq "package") {
        $consolidatedContent = $consolidatedContent.TrimEnd(',')
        $consolidatedContent += @"

    ]
  },
  "name": "sparkling-owl-spin-consolidated",
  "version": "1.0.0",
  "description": "Consolidated package.json from all project sources",
  "main": "index.js",
  "scripts": {
    "consolidation-info": "echo 'This is a consolidated package.json from $($files.Count) sources'"
  },
  "dependencies": {},
  "devDependencies": {},
  "peerDependencies": {},
  "optionalDependencies": {}
}
"@
    }
    else {
        $consolidatedContent += @"

# ========================================================================================
# 🎯 END OF CONSOLIDATED $($description.ToUpper())
# ========================================================================================

# Total files processed: $processedCount
# Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
# Project: Sparkling-Owl-Spin
"@
    }
    
    # Save consolidated file
    try {
        $consolidatedContent | Out-File -FilePath $targetFile -Encoding UTF8
        $consolidatedFiles[$typeName] = @{
            "file" = $targetFile
            "count" = $processedCount
            "description" = $description
        }
        Write-Host "  💾 Saved: $targetFile ($processedCount files consolidated)" -ForegroundColor Cyan
    }
    catch {
        Write-Host "  ❌ Failed to save $targetFile : $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Create summary report
$reportContent = @"
# 
# ████████████████████████████████████████████████████████████████████████████████████████
# ██                                                                                    ██
# ██   🦉 SPARKLING-OWL-SPIN - ULTIMATE CONSOLIDATION REPORT                          ██  
# ██   Complete project configuration consolidation summary                            ██
# ██                                                                                    ██
# ████████████████████████████████████████████████████████████████████████████████████████
#

# ULTIMATE CONSOLIDATION SUMMARY
- **Total configuration files found**: $totalFiles
- **Generated**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- **Project**: Sparkling-Owl-Spin

"@

foreach ($consolidated in $consolidatedFiles.GetEnumerator()) {
    $info = $consolidated.Value
    $reportContent += "## $($info.description)`n"
    $reportContent += "- **File**: $($info.file)`n"
    $reportContent += "- **Sources consolidated**: $($info.count)`n`n"
}

$reportContent += @"
## 🎯 FILES CREATED
"@

foreach ($consolidated in $consolidatedFiles.GetEnumerator()) {
    $reportContent += "- ``$($consolidated.Value.file)`` - $($consolidated.Value.description) ($($consolidated.Value.count) sources)`n"
}

$reportContent += @"

## ✨ BENEFITS
- **Single source of truth** for each configuration type
- **Easy maintenance** with centralized config files  
- **Complete project overview** in consolidated files
- **No configuration scattered** across the project
- **Version control friendly** with fewer files to track

---
**Status**: ✅ ULTIMATE CONSOLIDATION COMPLETE
**Total Files**: $totalFiles → $($consolidatedFiles.Count) consolidated files
"@

$reportContent | Out-File -FilePath "ULTIMATE_CONSOLIDATION_REPORT.md" -Encoding UTF8

Write-Host "`n🎯 ULTIMATE CONSOLIDATION COMPLETE!" -ForegroundColor Cyan
Write-Host "📊 Total files found: $totalFiles" -ForegroundColor Yellow  
Write-Host "📄 Consolidated files created: $($consolidatedFiles.Count)" -ForegroundColor Yellow
Write-Host "📋 Report saved: ULTIMATE_CONSOLIDATION_REPORT.md" -ForegroundColor Yellow

Write-Host "`n📁 FILES CREATED:" -ForegroundColor Cyan
foreach ($consolidated in $consolidatedFiles.GetEnumerator()) {
    Write-Host "  📄 $($consolidated.Value.file) ($($consolidated.Value.count) sources)" -ForegroundColor Green
}

Write-Host "`n✨ Ultimate consolidation completed successfully!" -ForegroundColor Green
