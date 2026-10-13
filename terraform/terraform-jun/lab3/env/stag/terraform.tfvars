project_name = "tf-lab3"
environment  = "stag"
applications = {
  web = {
    enabled        = true
    image          = "nginx:alpine"
    replicas       = 1
    container_port = 80
    service_port   = 80
    html_content   = <<-HTML
    <!doctype html>
    <html lang="vi">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Terraform Lab 3</title>
      <style>
        body {
          margin: 0;
          font-family: Arial, sans-serif;
          background: #f2f4f7;
          color: #1f2937;
        }

        main {
          max-width: 700px;
          margin: 80px auto;
          padding: 32px;
          background: white;
          border-radius: 12px;
          box-shadow: 0 4px 16px #00000018;
          text-align: center;
        }

        h1 {
          color: #2563eb;
        }

        .status {
          display: inline-block;
          margin-top: 16px;
          padding: 8px 16px;
          background: #dcfce7;
          color: #166534;
          border-radius: 999px;
        }
      </style>
    </head>
    <body>
      <main>
        <h1>Terraform Lab 3</h1>
        <p>Website này được triển khai bằng Terraform trên Kubernetes.</p>
        <p>Atlantis sẽ quản lý thay đổi thông qua Merge Request.</p>
        <div class="status">Application is running</div>
      </main>
    </body>
    </html>
    HTML
  }

  api = {
    enabled        = false
    image          = "nginx:alpine"
    replicas       = 1
    container_port = 80
    service_port   = 8080
    html_content   = ""
  }

  worker = {
    enabled        = false
    image          = "nginx:alpine"
    replicas       = 1
    container_port = 80
    service_port   = 8081
    html_content   = ""
  }
}
