output "namespace_name" {
  description = "Namespace is created"
  value       = kubernetes_namespace_v1.this.metadata[0].name
}