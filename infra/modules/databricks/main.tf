resource "azurerm_databricks_workspace" "this" {
  name                = "dbw-migration-${var.environment}"
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "premium"
  tags                = var.tags
}

output "workspace_url" {
  value = azurerm_databricks_workspace.this.workspace_url
}

output "workspace_id" {
  value = azurerm_databricks_workspace.this.workspace_id
}
