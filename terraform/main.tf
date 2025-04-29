terraform {
  required_providers {
    aiven = {
      source  = "aiven/aiven"
      version = "~> 4.0"
    }
  }
}

provider "aiven" {
  api_token = var.aiven_api_token
}

resource "aiven_kafka" "clickstream_kafka" {
  project                 = var.project_name
  cloud_name              = var.region-zone
  plan                    = var.plan_type_startup_2
  service_name            = var.kafka_service_name
  maintenance_window_dow  = "monday"
  maintenance_window_time = "10:00:00"

  kafka_user_config {
    kafka_rest      = true
    schema_registry = true
    kafka_version   = "3.8"

    kafka {
      group_max_session_timeout_ms = 70000
      log_retention_bytes          = 1000000000
    }

    kafka_authentication_methods {
      certificate = true
      sasl        = false
    }
  }

  timeouts {
    create = "30m"
    update = "20m"
    delete = "20m"
  }
}

resource "aiven_kafka_topic" "clickstream_events" {
  project      = var.project_name
  service_name = aiven_kafka.clickstream_kafka.service_name
  topic_name   = var.kafka_topic_name
  partitions   = 3
  replication  = 2

  timeouts {
    create = "10m"
    update = "10m"
    delete = "10m"
  }
}

resource "aiven_pg" "clickstream_pg" {
  project                 = var.project_name
  cloud_name              = var.region-zone
  plan                    = var.plan_type_startup_4
  service_name            = var.pg_db_name
  maintenance_window_dow  = "monday"
  maintenance_window_time = "10:00:00"

  pg_user_config {
    pg_version = "14"
  }

  timeouts {
    create = "10m"
    update = "10m"
    delete = "10m"
  }
}

resource "aiven_opensearch" "clickstream_os" {
  project                 = var.project_name
  cloud_name              = var.region-zone
  plan                    = var.plan_type_startup_4
  service_name            = var.os_name
  maintenance_window_dow  = "monday"
  maintenance_window_time = "10:00:00"

  opensearch_user_config {
    opensearch_version = "2"
  }

  timeouts {
    create = "10m"
    update = "10m"
    delete = "10m"
  }
}