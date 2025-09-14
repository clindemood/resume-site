# Deployment

This project can be hosted on Microsoft Azure using container-based services such as Azure Container Apps or Azure App Service. The instructions below use Azure Container Registry (ACR), Azure Container Apps, Azure DNS, and Azure CLI commands. Terraform equivalents are included for those preferring infrastructure as code.

## Prerequisites

- An Azure subscription with permissions to create resource groups, container registries, container apps, and DNS records.
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed and logged in via `az login`.
- Docker installed.
- (Optional) [Terraform](https://developer.hashicorp.com/terraform/downloads) installed.

## Build and push the image

1. Create a resource group and container registry.

   ```bash
   az group create --name resume-rg --location eastus
   az acr create --resource-group resume-rg --name resumeRegistry --sku Basic
   ```

2. Build the container image and push it to ACR.

   ```bash
   docker build -t resume-site:latest .
   az acr login --name resumeRegistry
   docker tag resume-site:latest resumeregistry.azurecr.io/resume-site:latest
   docker push resumeregistry.azurecr.io/resume-site:latest
   ```

## Deploy to Azure Container Apps

1. Create a Container Apps environment and deploy the image.

   ```bash
   az containerapp env create --name resume-env --resource-group resume-rg --location eastus

   az containerapp create \
     --name resume-app \
     --resource-group resume-rg \
     --environment resume-env \
     --image resumeregistry.azurecr.io/resume-site:latest \
     --target-port 80 \
     --ingress external \
     --registry-server resumeregistry.azurecr.io \
     --query properties.configuration.ingress.fqdn
   ```

   The command outputs the public FQDN of the running application. If you prefer Azure App Service, replace the above with `az webapp create --plan <plan> --name resume-app --deployment-container-image-name resumeregistry.azurecr.io/resume-site:latest`.

## Configure DNS

Point a domain to the deployed application using Azure DNS.

```bash
az network dns zone create --resource-group resume-rg --name example.com
az network dns record-set cname create --resource-group resume-rg --zone-name example.com --name resume
az network dns record-set cname add-record --resource-group resume-rg --zone-name example.com --record-set-name resume --cname <app-fqdn>
```

## Terraform provisioning (optional)

The following Terraform configuration replicates the above Azure CLI steps:

```hcl
provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = "resume-rg"
  location = "eastus"
}

resource "azurerm_container_registry" "acr" {
  name                = "resumeRegistry"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "Basic"
  admin_enabled       = true
}

resource "azurerm_container_app_environment" "env" {
  name                = "resume-env"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_container_app" "app" {
  name                         = "resume-app"
  container_app_environment_id = azurerm_container_app_environment.env.id
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"

  template {
    container {
      name   = "resume"
      image  = "${azurerm_container_registry.acr.login_server}/resume-site:latest"
      resources {
        cpu    = 0.25
        memory = "0.5Gi"
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = 80
  }
}
```

Apply the configuration:

```bash
terraform init
terraform apply
```

## Scaling and rolling out updates

- To scale the service: `az containerapp update --name resume-app --resource-group resume-rg --scale-rules '{"name":"cpu","custom":{"type":"cpu","metadata":{"threshold":"60"}}}'`
- To deploy a new image: rebuild and push the image, then run `az containerapp update --name resume-app --resource-group resume-rg --image resumeregistry.azurecr.io/resume-site:latest`

## Clean up

Destroy all resources when finished:

```bash
az group delete --name resume-rg --yes --no-wait
```

Or, if using Terraform:

```bash
terraform destroy
```

This removes the container app, registry, DNS zone, and resource group to prevent ongoing charges.
