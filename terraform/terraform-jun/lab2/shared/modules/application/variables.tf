variable "name" {
  description = "Ten deployment"
  type        = string
}

variable "namespace" {
  description = "Ten namespace"
  type        = string
}

variable "image" {
  description = "Ten image"
  type        = string
}

variable "replicas" {
  description = "so luong replicas"
  type        = number

  validation {
    condition = var.replicas >= 1

    error_message = "Replicas phai >= 1"
  }
}

variable "container_port" {
  description = "Container port"
  type        = number
}

variable "service_port" {
  description = "Service Port"
  type        = number
}

variable "labels" {
  description = "Labels"
  type        = map(string)
  default     = {}
}