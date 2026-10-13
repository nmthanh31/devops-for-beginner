output "namespace_name" {
  description = "Ten Kubernetes Namespace cua moi truong"
  value       = module.namespace.namespace_name
}

output "deployment_names" {
  description = "Tên Deployment theo từng application"

  value = {
    for name, application in module.application :
    name => application.deployment_name
  }
}

output "service_names" {
  description = "Tên Service theo từng application"

  value = {
    for name, application in module.application :
    name => application.service_name
  }
}
