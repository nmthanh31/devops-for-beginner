output "namespace_name" {
  description = "Tên Namespace"
  value       = module.platform.namespace_name
}

output "deployment_names" {
  description = "Tên Deployment theo từng application"
  value       = module.platform.deployment_names
}

output "service_names" {
  description = "Tên Service theo từng application"
  value       = module.platform.service_names
}