# Infrastructure as Code (Terraform)

This directory contains the Terraform modules used to provision the Azure and Databricks resources required for the migration accelerator.

## 🏗️ Provisioned Resources

The modules provision the following high-level components:

- **Azure Storage (ADLS Gen2)**: Storage accounts with hierarchical namespace enabled for the landing, bronze, silver, and gold layers.
- **Azure Databricks Workspace**: A premium workspace integrated with Unity Catalog.
- **Azure Key Vault**: For secure storage of Snowflake credentials, service principal secrets, and storage access keys.
- **Unity Catalog Metastore**: Configuration for the account-level metastore and its assignment to the workspace.
- **Networking**: Optional VNet injection and private endpoints (depending on variable configuration).

## 🚀 How to Deploy

Ensure you have the Azure CLI installed and are authenticated:
```bash
az login
```

### 1. Initialize Terraform
```bash
terraform init
```

### 2. Plan Deployment
Create a `terraform.tfvars` file based on the `variables.tf` definitions, then run:
```bash
terraform plan -out=tfplan
```

### 3. Apply Changes
```bash
terraform apply tfplan
```

## ⚙️ Variables

| Variable | Description | Type | Default |
| -------- | ----------- | ---- | ------- |
| `resource_group_name` | The name of the resource group to create. | `string` | - |
| `location` | Azure region for resources. | `string` | `East US` |
| `environment` | Environment tag (e.g., dev, prod). | `string` | `dev` |
| `databricks_sku` | The pricing tier for Databricks. | `string` | `premium` |
| `storage_account_name` | Name of the ADLS Gen2 account. | `string` | - |

## 🔒 Security and State
- **State Management**: It is highly recommended to use a remote backend (e.g., Azure Blob Storage) for `terraform.tfstate`.
- **Identity**: The modules use Managed Identities and RBAC roles to grant Databricks access to ADLS Gen2 without using account keys where possible.
