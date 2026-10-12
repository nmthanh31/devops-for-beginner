variable "kubeconfig_path" {
  description = "Kubeconfig Path"
  type        = string
}

variable "kube_context" {
  description = "Kubernetes context"
  type        = string
}

variable "project_name" {
  description = "Ten project"
  type        = string
}

variable "environment" {
  description = "environment"
  type        = string
}

variable "applications" {
  description = "application in dev environment"
  type = map(object({
    enabled        = bool
    image          = string
    replicas       = number
    container_port = number
    service_port   = number
  }))
}