locals {
  namespace_name = "${var.project_name}-${var.environment}"

  common_labels = {
    "managed-by" = "terraform"
    project      = var.project_name
    environment  = var.environment
  }

  enabled_applications = {
    for name, config in var.applications :
    name => config
    if config.enabled
  }
}

