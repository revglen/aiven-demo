variable "aiven_api_token" {
  description = "Avien API Token"
  type        = string
  sensitive   = true
}

variable "project_name" {
  description = "Aiven Project Name"
  type        = string
  sensitive   = false
  default     = "avien-demo"
}

variable "region-zone" {
  description = "The region and zone"
  type        = string
  default     = "aws-eu-west-1"
}

variable "plan_type_startup_2" {
  description = "The Avien plan to be used"
  type        = string
  default     = "startup-2"
}

variable "plan_type_startup_4" {
  description = "The Avien plan to be used"
  type        = string
  default     = "startup-4"
}

variable "kafka_service_name" {
  description = "The Avien Kafka Name"
  type        = string
  default     = "clickstream-kafka"
}

variable "kafka_topic_name" {
  description = "The Avien Kafka Topic Name"
  type        = string
  default     = "clickstream_events"
}

variable "pg_db_name" {
  description = "The Avien Postgres Database Name"
  type        = string
  default     = "clickstream-pg"
}

variable "os_name" {
  description = "The Avien OpenSearch Name"
  type        = string
  default     = "clickstream-os"
}

