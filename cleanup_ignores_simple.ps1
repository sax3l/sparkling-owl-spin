# PowerShell script to remove all old ignore files
Write-Host "Removing old ignore files..." -ForegroundColor Red

# Get all ignore files except the main .gitignore in root
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

$removedCount = 0
foreach ($file in $allFilesToRemove) {
    if (Test-Path $file) {
        Write-Host "Removing: $file" -ForegroundColor Gray
        Remove-Item $file -Force
        $removedCount++
    }
}

Write-Host "Removed $removedCount ignore files" -ForegroundColor Green
