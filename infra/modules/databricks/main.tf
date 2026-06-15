resource "azurerm_databricks_workspace" "this" {
  name                = "dbw-migration-${var.environment}"
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "premium" # Required for Unity Catalog
}

# Example Unity Catalog Catalog creation (requires databricks provider configured with workspace URL)
# resource "databricks_catalog" "migration" {
#   name         = "migration_${var.environment}"
#   comment      = "Migration catalog for ${var.environment}"
#   storage_root = "abfss://gold@${var.storage_account_name}.dfs.core.windows.net/"
# }
