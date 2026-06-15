# modules/storage/main.tf
resource "azurerm_storage_account" "this" {
  name                     = "stmigration${var.environment}001"
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled           = true
  tags                     = var.tags
}

resource "azurerm_storage_container" "containers" {
  for_each              = toset(["landing", "bronze", "silver", "gold", "checkpoints", "logs"])
  name                  = each.key
  storage_account_name  = azurerm_storage_account.this.name
  container_access_type = "private"
}

output "storage_account_id" {
  value = azurerm_storage_account.this.id
}
