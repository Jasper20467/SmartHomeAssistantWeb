# Build Test Script for Frontend Container
# This script helps verify that the frontend container builds properly
param(
    [string]$BuildContext = "frontend" # Path to build context (frontend directory)
)

Write-Host "Building frontend container with fixed configuration..." -ForegroundColor Cyan

# Make sure we're in the project root
$projectRoot = Split-Path -Parent $PSScriptRoot

# Check if the Azure nginx configuration exists in the frontend directory
if (-not (Test-Path "$projectRoot\$BuildContext\nginx.azure.conf")) {
    Write-Host "ERROR: nginx.azure.conf not found in $BuildContext directory" -ForegroundColor Red
    Write-Host "Make sure to copy nginx.azure.conf from docker directory to $BuildContext directory" -ForegroundColor Yellow
    exit 1
}

# Check if the local nginx configuration exists in the frontend directory
if (-not (Test-Path "$projectRoot\$BuildContext\nginx.conf")) {
    Write-Host "ERROR: nginx.conf not found in $BuildContext directory" -ForegroundColor Red
    exit 1
}

# Build the frontend container
Write-Host "Building frontend container..." -ForegroundColor Yellow
docker build -f "$projectRoot\docker\frontend.Dockerfile" -t smarthomeassistant-frontend-test "$projectRoot\$BuildContext"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Container built successfully!" -ForegroundColor Green
    
    # Test run the container
    Write-Host "`nTesting container with different environment configurations:" -ForegroundColor Cyan
    Write-Host "1) Local mode (no BACKEND_URL): docker run --rm -p 8080:80 smarthomeassistant-frontend-test" -ForegroundColor Yellow
    Write-Host "2) Azure mode (with BACKEND_URL): docker run --rm -p 8080:80 -e \"BACKEND_URL=http://some-backend-url\" smarthomeassistant-frontend-test" -ForegroundColor Yellow
    
    Write-Host "`nFor a full test, run:" -ForegroundColor Cyan
    Write-Host ".\scripts\test_frontend_container.ps1 -TestType local" -ForegroundColor Yellow
    Write-Host ".\scripts\test_frontend_container.ps1 -TestType azure" -ForegroundColor Yellow
} else {
    Write-Host "❌ Container build failed!" -ForegroundColor Red
}
