variable "name" {
  description = "namespace"
  type        = string
}

variable "labels" {
  description = "labels"
  type        = map(string)
  default     = {}
}