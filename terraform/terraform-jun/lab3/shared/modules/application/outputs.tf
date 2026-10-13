output "deployment_name" {
  description = "Deployment has been created"
  value       = kubernetes_deployment_v1.this.metadata[0].name
}

output "service_name" {
  description = "Service has been created"
  value       = kubernetes_service_v1.this.metadata[0].name
}