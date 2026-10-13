locals {
  labels_deployment = merge(var.labels, {
    app = var.name
  })
}

resource "kubernetes_deployment_v1" "this" {
  metadata {
    name      = var.name
    namespace = var.namespace
    labels    = local.labels_deployment
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
        labels = local.labels_deployment
      }

      spec {
        container {
          name  = var.name
          image = var.image
          port {
            container_port = var.container_port
          }
          volume_mount {
            name       = "web-content"
            mount_path = "/usr/share/nginx/html/index.html"
            sub_path   = "index.html"
            read_only  = true
          }
        }
        volume {
          name = "web-content"

          config_map {
            name = kubernetes_config_map_v1.web_content.metadata[0].name
          }
        }
      }
    }
  }
}

resource "kubernetes_service_v1" "this" {
  metadata {
    labels    = local.labels_deployment
    name      = var.name
    namespace = var.namespace
  }

  spec {
    type = "ClusterIP"
    selector = {
      app = var.name
    }
    port {
      port        = var.service_port
      target_port = var.container_port
    }
  }
}

resource "kubernetes_config_map_v1" "web_content" {
  metadata {
    name      = "${var.name}-content"
    namespace = var.namespace
    labels    = var.labels
  }

  data = {
    "index.html" = var.html_content
  }
}
