variable "applications" {
  description = "List of applications"

  type = map(object({
    enabled        = bool
    image          = string
    replicas       = number
    container_port = number
    service_port   = number
    html_content   = string
  }))
}

variable "project_name" {
  description = "project name"
  type        = string
}

variable "environment" {
  description = "environment"
  type        = string

  validation {
    condition     = contains(["dev", "stag"], var.environment)
    error_message = "Environment must be dev or stag"
  }
}
