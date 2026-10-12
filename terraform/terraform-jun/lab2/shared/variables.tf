variable "applications" {
  description = "Danh sách các ứng dụng triển khai"

  type = map(object({
    enabled        = bool
    image          = string
    replicas       = number
    container_port = number
    service_port   = number
  }))
}

variable "project_name" {
  description = "Tên của project"
  type        = string
}

variable "environment" {
  description = "Tên môi trường triển khai"
  type        = string
  validation {
    condition = contains(
      ["dev", "stag"],
      var.environment
    )

    error_message = "environment chỉ được phép là dev hoặc stag"
  }
}