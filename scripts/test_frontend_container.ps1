# Test Frontend Container with Different Environments
# This script helps verify the frontend container works in both local and Azure modes
param(
    [string]$TestType = "local" # Can be "local" or "azure"
)

Write-Host "Testing frontend container in $TestType mode..." -ForegroundColor Cyan

# Make sure we're in the project root
$projectRoot = Split-Path -Parent $PSScriptRoot

# Build the frontend container
Write-Host "Building frontend container..." -ForegroundColor Yellow
docker build -f "$projectRoot\docker\frontend.Dockerfile" -t smarthomeassistant-frontend-test "$projectRoot\frontend"

# Run the container with different configurations based on test type
if ($TestType -eq "local") {
    # Test in local mode (no BACKEND_URL environment variable)
    Write-Host "Running container in local Docker Compose mode (using 'backend' service name)" -ForegroundColor Green
    docker run --rm -p 8080:80 --name frontend-test smarthomeassistant-frontend-test

} elseif ($TestType -eq "azure") {
    # Test in Azure mode (with BACKEND_URL environment variable)
    Write-Host "Running container in Azure Container Apps mode (using BACKEND_URL)" -ForegroundColor Green
    docker run --rm -p 8080:80 -e "BACKEND_URL=http://localhost:8000" --name frontend-test smarthomeassistant-frontend-test
} else {
    Write-Host "Invalid test type. Use 'local' or 'azure'" -ForegroundColor Red
    exit 1
}

# You can access the container at http://localhost:8080
Write-Host "Container is running at http://localhost:8080" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the container" -ForegroundColor Yellow
