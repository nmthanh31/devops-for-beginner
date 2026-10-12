project_name    = "tf-lab2"
environment     = "stag"
kubeconfig_path = "../../../../k8s-config/local-rancher.yaml"
kube_context    = "local"

applications = {
  frontend = {
    enabled        = true
    image          = "nginx:alpine"
    replicas       = 1
    container_port = 80
    service_port   = 80
  }

  api = {
    enabled        = true
    image          = "nginx:alpine"
    replicas       = 1
    container_port = 80
    service_port   = 8080
  }

  worker = {
    enabled        = false
    image          = "nginx:alpine"
    replicas       = 1
    container_port = 80
    service_port   = 8081
  }
}
