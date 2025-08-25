# PowerShell script to consolidate all ignore files into one .gitignore
# This script will find all .gitignore, .dockerignore, .prettierignore and other ignore files and merge them

Write-Host "🦉 Consolidating all ignore files..." -ForegroundColor Green

# Get all different types of ignore files
$gitignoreFiles = Get-ChildItem -Path "." -Recurse -Name ".gitignore" | 
    Where-Object { (Split-Path $_ -Parent) -ne "." }

$dockerignoreFiles = Get-ChildItem -Path "." -Recurse -Name ".dockerignore"
$prettierignoreFiles = Get-ChildItem -Path "." -Recurse -Name ".prettierignore"
$otherIgnoreFiles = Get-ChildItem -Path "." -Recurse -Name "*ignore" | 
    Where-Object { $_ -notmatch "\.gitignore$" -and $_ -notmatch "\.dockerignore$" -and $_ -notmatch "\.prettierignore$" }

$allIgnoreFiles = @()
$allIgnoreFiles += $gitignoreFiles
$allIgnoreFiles += $dockerignoreFiles
$allIgnoreFiles += $prettierignoreFiles
$allIgnoreFiles += $otherIgnoreFiles

Write-Host "Found $($allIgnoreFiles.Count) ignore files:" -ForegroundColor Yellow
Write-Host "  .gitignore files: $($gitignoreFiles.Count)" -ForegroundColor Cyan
Write-Host "  .dockerignore files: $($dockerignoreFiles.Count)" -ForegroundColor Cyan
Write-Host "  .prettierignore files: $($prettierignoreFiles.Count)" -ForegroundColor Cyan
Write-Host "  Other ignore files: $($otherIgnoreFiles.Count)" -ForegroundColor Cyan

# Create a hashtable to store unique ignore patterns
$ignorePatterns = @{}
$allContent = @()

# Add header
$allContent += "# "
$allContent += "# ████████████████████████████████████████████████████████████████████████████████████████"
$allContent += "# ██                                                                                    ██"
$allContent += "# ██   🦉 SPARKLING-OWL-SPIN - CONSOLIDATED .GITIGNORE                                 ██"
$allContent += "# ██   All Ignore Patterns from Vendors, Agents, Engines & Core                       ██"
$allContent += "# ██                                                                                    ██"
$allContent += "# ████████████████████████████████████████████████████████████████████████████████████████"
$allContent += "#"
$allContent += ""

# Process each ignore file
foreach ($file in $allIgnoreFiles) {
    Write-Host "Processing: $file" -ForegroundColor Gray
    
    if (Test-Path $file) {
        $content = Get-Content $file -ErrorAction SilentlyContinue -Encoding UTF8
        
        if ($content) {
            $allContent += "# From: $file"
            
            foreach ($line in $content) {
                $line = $line.Trim()
                
                # Skip empty lines
                if ($line -eq "") {
                    $allContent += ""
                    continue
                }
                
                # Add comments as-is
                if ($line.StartsWith("#")) {
                    $allContent += $line
                    continue
                }
                
                # Only add unique patterns
                $pattern = $line.ToLower()
                if (-not $ignorePatterns.ContainsKey($pattern)) {
                    $ignorePatterns[$pattern] = $line
                    $allContent += $line
                }
            }
            
            $allContent += ""
        }
    }
}

# Add footer
$allContent += "# ========================================================================================"
$allContent += "# 🎯 END OF CONSOLIDATED IGNORE PATTERNS"
$allContent += "# ========================================================================================"
$allContent += ""
$allContent += "# Total unique patterns: $($ignorePatterns.Count)"
$allContent += "# Consolidated from $($allIgnoreFiles.Count) ignore files"
$allContent += "# Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

# Write consolidated ignore patterns to the main .gitignore
$allContent | Out-File -FilePath ".gitignore" -Encoding UTF8

Write-Host "✅ Consolidated $($ignorePatterns.Count) unique patterns into .gitignore" -ForegroundColor Green
Write-Host "📁 Processed $($allIgnoreFiles.Count) ignore files" -ForegroundColor Green

# Show summary
Write-Host "`n📊 Summary:" -ForegroundColor Yellow
Write-Host "  Total ignore files found: $($allIgnoreFiles.Count)" -ForegroundColor White
Write-Host "  Unique patterns consolidated: $($ignorePatterns.Count)" -ForegroundColor White
Write-Host "  Output file: .gitignore" -ForegroundColor White
