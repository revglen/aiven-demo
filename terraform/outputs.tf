# Kafka Connection Details
output "kafka_service_uri" {
  value     = aiven_kafka.clickstream_kafka.service_uri
  sensitive = true
}

output "kafka_host" {
  value     = aiven_kafka.clickstream_kafka.service_host
  sensitive = false
}

output "kafka_port" {
  value     = aiven_kafka.clickstream_kafka.service_port
  sensitive = false
}

# Kafka Password
output "kafka_password" {
  value     = aiven_kafka.clickstream_kafka.service_password
  sensitive = true
}

# PG Connection Details
output "pg_service_uri" {
  value     = aiven_pg.clickstream_pg.service_uri
  sensitive = true
}

output "pg_host" {
  value     = aiven_pg.clickstream_pg.service_host
  sensitive = false
}

output "pg_port" {
  value     = aiven_pg.clickstream_pg.service_port
  sensitive = false
}

output "pg_user" {
  value     = aiven_pg.clickstream_pg.service_username
  sensitive = false
}

# PostgreSQL Password
output "pg_password" {
  value     = aiven_pg.clickstream_pg.service_password
  sensitive = true
}

# OpenSearch Connection Details
output "os_service_uri" {
  value     = aiven_opensearch.clickstream_os.service_uri
  sensitive = true
}

output "os_host" {
  value     = aiven_opensearch.clickstream_os.service_host
  sensitive = false
}

output "os_port" {
  value     = aiven_opensearch.clickstream_os.service_port
  sensitive = false
}

output "os_user" {
  value     = aiven_opensearch.clickstream_os.service_username
  sensitive = false
}

# OpenSearch Password
output "os_password" {
  value     = aiven_opensearch.clickstream_os.service_password
  sensitive = true
}