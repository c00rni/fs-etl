terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "4.6.0"
    }
  }
}

provider "docker" {}

resource "docker_compose" "app" {
  project_name = "fs-etl"

  env_files = [
    "${path.module}/.env",
  ]

  config_paths = [
    "${path.module}/docker-compose.yaml",
  ]
}

