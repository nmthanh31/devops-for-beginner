variable "name" {
  description = "deployment, service name"
  type        = string
}

variable "namespace" {
  description = "namespace"
  type        = string
}

variable "labels" {
  description = "labels"
  type        = map(string)
  default     = {}
}

variable "image" {
  description = "image"
  type        = string
}

variable "replicas" {
  description = "replicas"
  type        = number
  validation {
    condition = var.replicas >= 1

    error_message = "Replicas must be greater than 1"
  }
}

variable "container_port" {
  description = "container_port"
  type        = number
}

variable "service_port" {
  description = "service_port"
  type        = number
}

variable "html_content" {
  description = "HTML content mounted into nginx"
  type        = string
}