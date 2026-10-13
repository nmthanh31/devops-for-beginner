variable "project_name" {
  description = "project name"
  type        = string
}

variable "environment" {
  description = "environment"
  type        = string
}

variable "applications" {
  description = "applications"
  type = map(object({
    enabled        = bool
    image          = string
    replicas       = number
    container_port = number
    service_port   = number
    html_content   = string
  }))
}
