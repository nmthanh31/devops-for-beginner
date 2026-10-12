provider "kubernetes" {
  config_path    = "~/.kube/config"
  config_context = "rancher"
}

resource "kubernetes_namespace" "example" {
  metadata {
    name = "example-terrafrom-ns"
  }
}

resource "kubernetes_deployment" "nginx_deploy" {
  metadata {
    name      = "nginx-deploy"
    namespace = "example-terrafrom-ns"

    labels = {
      app = "nginx"
    }
  }

  spec {
    replicas = 2
    selector {
      match_labels = {
        app = "nginx"
      }
    }
    template {
      metadata {
        labels = {
          app = "nginx"
        }
      }

      spec {
        container {
          name  = "nginx"
          image = "nginx:alpine"

          port {
            name           = "http"
            container_port = 80
            protocol       = "TCP"
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "nginx_service" {
  metadata {
    name      = "nginx-service"
    namespace = "example-terrafrom-ns"
  }

  spec {
    selector = {
      app = "nginx"
    }

    port {
      name        = "http"
      port        = 80
      target_port = 80
      protocol    = "TCP"
    }

    type = "ClusterIP"
  }
}