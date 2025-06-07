# Azure Container App Troubleshooting Script
# This script helps diagnose issues with the Smart Home Assistant Web application in Azure Container Apps

param(
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory = $true)]
    [string]$AppName
)

Write-Host "Checking Container Apps in $ResourceGroupName..."

# Get the container apps environment
$env = az containerapp env list --resource-group $ResourceGroupName --query "[0].name" -o tsv
Write-Host "Container Apps Environment: $env"

# Get the frontend container app status
Write-Host "`nFrontend Container App:"
az containerapp show `
    --resource-group $ResourceGroupName `
    --name "$($AppName)-frontend" `
    --query "{name:name, provisioningState:properties.provisioningState, fqdn:properties.configuration.ingress.fqdn, targetPort:properties.configuration.ingress.targetPort}" -o table

# Get the backend container app status
Write-Host "`nBackend Container App:"
az containerapp show `
    --resource-group $ResourceGroupName `
    --name "$($AppName)-backend" `
    --query "{name:name, provisioningState:properties.provisioningState, fqdn:properties.configuration.ingress.fqdn, targetPort:properties.configuration.ingress.targetPort}" -o table

# Get the frontend container app logs
Write-Host "`nFrontend Container App Logs:"
az containerapp logs show `
    --resource-group $ResourceGroupName `
    --name "$($AppName)-frontend" `
    --tail 50

# Check if there are any revision issues
Write-Host "`nFrontend Container App Revisions:"
az containerapp revision list `
    --resource-group $ResourceGroupName `
    --name "$($AppName)-frontend" `
    --query "[].{revisionName:name, state:properties.status, created:properties.createdTime, active:properties.active, replicas:properties.replicas}" -o table

# Update the frontend container app BACKEND_URL if it's wrong
$updateConfig = Read-Host "`nWould you like to update the frontend BACKEND_URL to point to the backend? (Y/N)"
if ($updateConfig -eq "Y" -or $updateConfig -eq "y") {
    $backendUrl = az containerapp show `
        --resource-group $ResourceGroupName `
        --name "$($AppName)-backend" `
        --query "properties.configuration.ingress.fqdn" -o tsv
    
    Write-Host "Updating frontend to use backend URL: https://$backendUrl"
    
    az containerapp update `
        --resource-group $ResourceGroupName `
        --name "$($AppName)-frontend" `
        --set-env-vars "BACKEND_URL=https://$backendUrl"
    
    Write-Host "Frontend BACKEND_URL updated. Restarting frontend container app..."
    
    az containerapp restart `
        --resource-group $ResourceGroupName `
        --name "$($AppName)-frontend"
        
    Write-Host "Frontend container app restarted. Please wait a few minutes for it to become available."
}
