variable "name" {
  description = "Tên Kubernetes Namespace"
  type        = string
}

variable "labels" {
  description = "Labels gắn vào Kubernetes Namespace"
  type        = map(string)
  default     = {}
}
