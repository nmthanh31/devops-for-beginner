provider "kubernetes" {
  config_path    = abspath(var.kubeconfig_path)
  config_context = var.kube_context
}