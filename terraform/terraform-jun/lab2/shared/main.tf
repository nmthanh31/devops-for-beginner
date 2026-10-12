module "namespace" {
  source = "./modules/namespace"

  name   = local.namespace_name
  labels = local.common_labels
}

module "application" {
  source = "./modules/application"

  for_each       = local.enabled_applications
  name           = each.key
  namespace      = module.namespace.name
  image          = each.value.image
  replicas       = each.value.replicas
  container_port = each.value.container_port
  service_port   = each.value.service_port
  labels         = local.common_labels
}