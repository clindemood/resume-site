terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
  tenant_id       = var.tenant_id
  client_id       = var.client_id
  client_secret   = var.client_secret
}

locals {
  frontdoor_host = "${var.app_name}-fd.azurefd.net"
}

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_container_registry" "main" {
  name                = var.registry_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = true
}

resource "azurerm_app_service_plan" "main" {
  name                = "${var.app_name}-plan"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  kind                = "Linux"
  reserved            = true

  sku {
    tier = "Basic"
    size = "B1"
  }
}

resource "azurerm_app_service" "main" {
  name                = var.app_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  app_service_plan_id = azurerm_app_service_plan.main.id

  site_config {
    linux_fx_version = "DOCKER|${azurerm_container_registry.main.login_server}/${var.app_name}:latest"
  }

  app_settings = {
    WEBSITES_ENABLE_APP_SERVICE_STORAGE = "false"
    DOCKER_REGISTRY_SERVER_URL          = "https://${azurerm_container_registry.main.login_server}"
    DOCKER_REGISTRY_SERVER_USERNAME     = azurerm_container_registry.main.admin_username
    DOCKER_REGISTRY_SERVER_PASSWORD     = azurerm_container_registry.main.admin_password
  }
}

resource "azurerm_storage_account" "logs" {
  name                     = var.log_storage_account_name
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "logs" {
  name                  = "logs"
  storage_account_name  = azurerm_storage_account.logs.name
  container_access_type = "private"
}

resource "azurerm_frontdoor" "main" {
  name                = "${var.app_name}-fd"
  resource_group_name = azurerm_resource_group.main.name

  backend_pool_settings {
    backend_pools_send_receive_timeout_seconds = 60
  }

  backend_pool {
    name = "backendPool"

    backend {
      host_header = azurerm_app_service.main.default_site_hostname
      address     = azurerm_app_service.main.default_site_hostname
      http_port   = 80
      https_port  = 443
      priority    = 1
      weight      = 50
    }

    load_balancing_name = "loadBalancingSettings"
    health_probe_name   = "healthProbeSettings"
  }

  frontend_endpoint {
    name      = "frontendEndpoint"
    host_name = local.frontdoor_host
  }

  routing_rule {
    name               = "routingRule"
    frontend_endpoints = ["frontendEndpoint"]
    accepted_protocols = ["Http", "Https"]
    patterns_to_match  = ["/*"]

    forwarding_configuration {
      backend_pool_name = "backendPool"
    }
  }

  load_balancing_settings {
    name                        = "loadBalancingSettings"
    sample_size                 = 4
    successful_samples_required = 2
  }

  health_probe_settings {
    name                = "healthProbeSettings"
    path                = "/"
    protocol            = "Https"
    interval_in_seconds = 30
  }
}

resource "azurerm_dns_zone" "main" {
  name                = var.domain_name
  resource_group_name = azurerm_resource_group.main.name
}

output "registry_url" {
  description = "Login server of the container registry"
  value       = azurerm_container_registry.main.login_server
}

output "app_endpoint" {
  description = "Endpoint for the application"
  value       = azurerm_frontdoor.main.frontend_endpoints[0].host_name
}

