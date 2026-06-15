# variables.tf
variable "environment" {
  type        = string
  description = "The environment for deployment (dev, prod)"
}

variable "location" {
  type        = string
  description = "Azure region for resources"
  default     = "East US"
}

variable "tags" {
  type        = map(string)
  description = "Resource tags"
  default = {
    Project = "Snowflake-Databricks-Migration"
    Owner   = "Data-Engineering"
  }
}
