module "platform" {
  source = "../../shared"

  project_name = var.project_name
  environment  = var.environment

  applications = var.applications
}