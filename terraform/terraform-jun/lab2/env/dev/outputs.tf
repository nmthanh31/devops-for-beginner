output "namespace_name" {
  description = "Ten ns"
  value       = module.platform.namespace_name
}

output "deployment_names" {
  description = "Tên Deployment theo từng application"

  value = {
    for name, application in module.platform :
    name => application.deployment_name
  }
}

output "service_names" {
  description = "Tên Service theo từng application"

  value = {
    for name, application in module.platform :
    name => application.service_name
  }
}