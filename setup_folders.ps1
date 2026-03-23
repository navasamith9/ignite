# setup_folders.ps1
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "IGNITE Project - Folder Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Creating folder structure..." -ForegroundColor Green

$folders = @(
    "templates",
    "templates\accounts",
    "templates\lhtc",
    "templates\bus",
    "templates\lostfound",
    "static",
    "static\css",
    "static\js",
    "media",
    "media\uploads",
    "accounts\migrations",
    "lhtc\migrations",
    "bus\migrations",
    "lostfound\migrations",
    "bus\templatetags"
)

foreach ($folder in $folders) {
    if (Test-Path $folder) {
        Write-Host "  ✓ Folder already exists: $folder" -ForegroundColor Yellow
    } else {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Host "  ✓ Created folder: $folder" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Creating templatetags files..." -ForegroundColor Green

if (Test-Path "bus\templatetags\__init__.py") {
    Write-Host "  ✓ __init__.py already exists" -ForegroundColor Yellow
} else {
    New-Item -Path "bus\templatetags\__init__.py" -ItemType File -Force | Out-Null
    Write-Host "  ✓ Created: bus\templatetags\__init__.py" -ForegroundColor Green
}

if (Test-Path "bus\templatetags\bus_filters.py") {
    Write-Host "  ✓ bus_filters.py already exists" -ForegroundColor Yellow
} else {
    New-Item -Path "bus\templatetags\bus_filters.py" -ItemType File -Force | Out-Null
    Write-Host "  ✓ Created: bus\templatetags\bus_filters.py" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Folder structure setup complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan