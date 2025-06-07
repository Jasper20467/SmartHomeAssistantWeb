# Azure Container App Deployment Script
# This script helps deploy the Smart Home Assistant Web application to Azure Container Apps
# with the correct service communication configuration.

param(
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory = $true)]
    [string]$AppName,
    
    [Parameter(Mandatory = $false)]
    [string]$Location = "eastus",
    
    [Parameter(Mandatory = $false)]
    [string]$ImageVersion = "1.0"
)

Write-Host "Deploying $AppName to Azure Container Apps in $ResourceGroupName..."

# Deploy the bicep template
az deployment group create `
    --resource-group $ResourceGroupName `
    --template-file ./main.bicep `
    --parameters appName=$AppName `
    --parameters location=$Location `
    --parameters imageVersion=$ImageVersion

# After deployment, verify the frontend URL and backend URL
$frontendUrl = az containerapp show `
    --resource-group $ResourceGroupName `
    --name "$($AppName)-frontend" `
    --query "properties.configuration.ingress.fqdn" -o tsv

$backendUrl = az containerapp show `
    --resource-group $ResourceGroupName `
    --name "$($AppName)-backend" `
    --query "properties.configuration.ingress.fqdn" -o tsv

Write-Host "Deployment completed!"
Write-Host "Frontend URL: https://$frontendUrl"
Write-Host "Backend URL: https://$backendUrl"
Write-Host ""
Write-Host "To check logs for the frontend container app:"
Write-Host "az containerapp logs show --resource-group $ResourceGroupName --name '$($AppName)-frontend'"

# Offer to open the frontend in a browser
$openBrowser = Read-Host "Would you like to open the frontend in a browser? (Y/N)"
if ($openBrowser -eq "Y" -or $openBrowser -eq "y") {
    Start-Process "https://$frontendUrl"
}
