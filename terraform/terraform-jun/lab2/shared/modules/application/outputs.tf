output "deployment_name" {
  description = "Tên Kubernetes deployment đã được tạo"
  value       = kubernetes_deployment_v1.this.metadata[0].name
}

output "service_name" {
  description = "Ten kubernetes service đã được tạo"
  value       = kubernetes_service_v1.this.metadata[0].name
}