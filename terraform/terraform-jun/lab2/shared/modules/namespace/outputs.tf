output "name" {
  description = "Tên Kubernetes Namespace đã được tạo"
  value       = kubernetes_namespace_v1.this.metadata[0].name
}