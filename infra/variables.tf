variable "environment" {
  type    = string
  default = "dev"
}
variable "location" {
  type    = string
  default = "East US"
}
variable "tags" {
  type = map(string)
  default = { Project = "Migration" }
}
