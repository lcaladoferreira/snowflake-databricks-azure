output "resource_group_name" {
  value       = azurerm_resource_group.this.name
  description = "The name of the Azure Resource Group"
}

output "storage_account_name" {
  value       = module.storage.storage_account_name
  description = "The name of the ADLS Gen2 Storage Account"
}

output "databricks_workspace_url" {
  value       = module.databricks.workspace_url
  description = "The URL of the Azure Databricks Workspace"
}

output "databricks_workspace_id" {
  value       = module.databricks.workspace_id
  description = "The ID of the Azure Databricks Workspace"
}

output "key_vault_uri" {
  value       = module.keyvault.key_vault_uri
  description = "The URI of the Azure Key Vault"
}
