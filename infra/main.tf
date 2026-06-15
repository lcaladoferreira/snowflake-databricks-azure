terraform {
  required_version = ">= 1.5.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.90"
    }
    databricks = {
      source = "databricks/databricks"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "this" {
  name     = "rg-migration-${var.environment}"
  location = var.location
  tags     = var.tags
}

module "storage" {
  source              = "./modules/storage"
  resource_group_name = azurerm_resource_group.this.name
  location            = azurerm_resource_group.this.location
  environment         = var.environment
  tags                = var.tags
}

module "keyvault" {
  source              = "./modules/keyvault"
  resource_group_name = azurerm_resource_group.this.name
  location            = azurerm_resource_group.this.location
  environment         = var.environment
  tags                = var.tags
}

module "databricks" {
  source              = "./modules/databricks"
  resource_group_name = azurerm_resource_group.this.name
  location            = azurerm_resource_group.this.location
  environment         = var.environment
  storage_account_id  = module.storage.storage_account_id
  tags                = var.tags
}
