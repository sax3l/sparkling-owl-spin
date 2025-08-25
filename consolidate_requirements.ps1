# PowerShell script to consolidate all requirements files into one
# This script will find all requirements*.txt files and merge them

Write-Host "🦉 Consolidating all requirements files..." -ForegroundColor Green

# Get all requirements files
$requirementsFiles = Get-ChildItem -Path "." -Recurse -Name "requirements*.txt" | 
    Where-Object { $_ -notmatch "requirements\.txt$" -or (Split-Path (Split-Path $_) -Leaf) -ne "." } |
    Sort-Object

Write-Host "Found $($requirementsFiles.Count) requirements files:" -ForegroundColor Yellow
$requirementsFiles | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }

# Create a hashtable to store unique packages
$packages = @{}
$allContent = @()

# Add header
$allContent += "# "
$allContent += "# ████████████████████████████████████████████████████████████████████████████████████████"
$allContent += "# ██                                                                                    ██"
$allContent += "# ██   🦉 SPARKLING-OWL-SPIN - CONSOLIDATED REQUIREMENTS                               ██"
$allContent += "# ██   All Dependencies from Vendors, Agents, Engines & Core                         ██"
$allContent += "# ██                                                                                    ██"
$allContent += "# ████████████████████████████████████████████████████████████████████████████████████████"
$allContent += "#"
$allContent += ""

# Process each requirements file
foreach ($file in $requirementsFiles) {
    Write-Host "Processing: $file" -ForegroundColor Cyan
    
    if (Test-Path $file) {
        $content = Get-Content $file -ErrorAction SilentlyContinue
        
        if ($content) {
            $allContent += "# From: $file"
            
            foreach ($line in $content) {
                $line = $line.Trim()
                
                # Skip empty lines and comments
                if ($line -eq "" -or $line.StartsWith("#")) {
                    continue
                }
                
                # Extract package name (before == or >= or <= etc.)
                if ($line -match "^([a-zA-Z0-9_-]+)") {
                    $packageName = $matches[1].ToLower()
                    
                    # Only add if we haven't seen this package before
                    if (-not $packages.ContainsKey($packageName)) {
                        $packages[$packageName] = $line
                        $allContent += $line
                    }
                }
            }
            
            $allContent += ""
        }
    }
}

# Add footer
$allContent += "# ========================================================================================"
$allContent += "# 🎯 END OF CONSOLIDATED REQUIREMENTS"
$allContent += "# ========================================================================================"
$allContent += ""
$allContent += "# Total unique packages: $($packages.Count)"
$allContent += "# Consolidated from $($requirementsFiles.Count) requirements files"
$allContent += "# Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

# Write consolidated requirements to the main requirements.txt
$allContent | Out-File -FilePath "requirements.txt" -Encoding UTF8

Write-Host "✅ Consolidated $($packages.Count) unique packages into requirements.txt" -ForegroundColor Green
Write-Host "📁 Processed $($requirementsFiles.Count) requirements files" -ForegroundColor Green

# Show summary
Write-Host "`n📊 Summary:" -ForegroundColor Yellow
Write-Host "  Total requirements files found: $($requirementsFiles.Count)" -ForegroundColor White
Write-Host "  Unique packages consolidated: $($packages.Count)" -ForegroundColor White
Write-Host "  Output file: requirements.txt" -ForegroundColor White
