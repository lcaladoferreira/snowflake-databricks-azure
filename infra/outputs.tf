output "resource_group_name" {
  value = azurerm_resource_group.this.name
}

output "storage_account_id" {
  value = module.storage.storage_account_id
}
