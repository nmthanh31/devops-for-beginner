variable "kubeconfig_path" {
  description = "kubeconfig path"
  type        = string
}

variable "kube_context" {
  description = "kube context"
  type        = string
}

variable "project_name" {
  description = "project name"
  type        = string
}

variable "environment" {
  description = "environment"
  type        = string
}

variable "applications" {
  description = "applications in stag environment"
  type = map(object({
    enabled        = bool
    image          = string
    replicas       = number
    container_port = number
    service_port   = number
  }))
}