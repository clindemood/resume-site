variable "subscription_id" {
  description = "Azure subscription ID."
  type        = string
}

variable "tenant_id" {
  description = "Azure tenant ID."
  type        = string
}

variable "client_id" {
  description = "Azure client ID for authentication."
  type        = string
}

variable "client_secret" {
  description = "Azure client secret for authentication."
  type        = string
  sensitive   = true
}

variable "location" {
  description = "Azure region to deploy resources."
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group to create or use."
  type        = string
}

variable "registry_name" {
  description = "Name for the Azure Container Registry."
  type        = string
}

variable "app_name" {
  description = "Name of the App Service."
  type        = string
}

variable "log_storage_account_name" {
  description = "Name of the storage account for logs."
  type        = string
}

variable "domain_name" {
  description = "Domain name for the DNS zone."
  type        = string
}
