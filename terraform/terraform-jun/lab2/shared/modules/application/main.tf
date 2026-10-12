locals {
  pod_labels = merge(var.labels, {
    app = var.name
  })
}

resource "kubernetes_deployment_v1" "this" {
  metadata {
    name      = var.name
    labels    = local.pod_labels
    namespace = var.namespace
  }

  spec {
    replicas = var.replicas
    selector {
      match_labels = {
        app = var.name
      }
    }
    template {
      metadata {
        labels = local.pod_labels
      }

      spec {
        container {
          image = var.image
          name  = var.name

          port {
            name           = "http"
            container_port = var.container_port
          }
        }
      }
    }
  }
}

resource "kubernetes_service_v1" "this" {
  metadata {
    name      = "${var.name}-service"
    namespace = var.namespace
    labels    = local.pod_labels
  }
  spec {
    selector = {
      app = var.name
    }

    type = "ClusterIP"

    port {
      name        = "http"
      port        = var.service_port
      target_port = var.container_port
      protocol    = "TCP"
    }
  }
}