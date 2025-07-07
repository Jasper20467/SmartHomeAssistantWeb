# Quick Docker Push Script
# Usage: .\quick_push.ps1 [version]

param(
    [string]$Version = (Get-Date -Format "yyyy.MM.dd.HHmm")
)

# Docker Hub Settings
$DOCKER_USERNAME = "popo510691"

# Image Configuration
$services = @(
    @{ name = "frontend"; image = "homeassistant.frontend"; dockerfile = "../docker/frontend.Dockerfile"; context = "../frontend" },
    @{ name = "backend"; image = "homeassistant.backend"; dockerfile = "../docker/backend.Dockerfile"; context = "../backend" },
    @{ name = "linebot"; image = "homeassistant.linebot"; dockerfile = "../docker/linebot.Dockerfile"; context = ".." }
)

Write-Host "Quick Docker Push to Docker Hub" -ForegroundColor Magenta
Write-Host "Version: $Version" -ForegroundColor Blue
Write-Host ""

# Confirm push
$confirm = Read-Host "Continue? (Y/n)"
if ($confirm -match "^[Nn]$") {
    Write-Host "Cancelled" -ForegroundColor Yellow
    exit
}

$startTime = Get-Date
$failed = @()
$success = @()

foreach ($service in $services) {
    $imageName = "$DOCKER_USERNAME/$($service.image)"
    
    Write-Host "Processing $($service.name)..." -ForegroundColor Cyan
    
    try {
        # Build
        Write-Host "   Building..." -ForegroundColor Yellow
        docker build -f $service.dockerfile -t "${imageName}:${Version}" -t "${imageName}:latest" $service.context | Out-Null
        
        # Push version tag
        Write-Host "   Pushing $Version..." -ForegroundColor Yellow
        docker push "${imageName}:${Version}" | Out-Null
        
        # Push latest tag
        Write-Host "   Pushing latest..." -ForegroundColor Yellow
        docker push "${imageName}:latest" | Out-Null
        
        Write-Host "   Completed" -ForegroundColor Green
        $success += $service.name
    }
    catch {
        Write-Host "   Failed: $($_.Exception.Message)" -ForegroundColor Red
        $failed += $service.name
    }
    Write-Host ""
}

$duration = (Get-Date) - $startTime
Write-Host "Total time: $([math]::Round($duration.TotalMinutes, 1)) minutes" -ForegroundColor Blue

if ($success.Count -gt 0) {
    Write-Host "Success: $($success -join ', ')" -ForegroundColor Green
}

if ($failed.Count -gt 0) {
    Write-Host "Failed: $($failed -join ', ')" -ForegroundColor Red
}

Write-Host ""
Write-Host "Docker Hub: https://hub.docker.com/u/$DOCKER_USERNAME" -ForegroundColor Cyan
