#!/bin/bash

set -e

PROJECT="avien-demo"
SERVICE_NAME="clickstream-kafka"
DEST_DIR="./certs"
ENV_FILE=".env"

echo "⏳ Cleaning up any Terraform and/or Cert folders and .env file"
rm -rf ./.terraform || true
rm -rf $DEST_DIR || true
rm -rf $ENV_FILE || true

echo "⏳ Running Terraform to deply assets to Avien Platform..."
terraform init
terraform apply -auto-approve

echo "✅ Terraform deploying assets to Avien Platform"

echo "⏳ Waiting for Kafka service to become RUNNING..."
while true; do
  STATUS=$(avn service get "$SERVICE_NAME" --project "$PROJECT" --json | jq -r '.state')
  echo "Current status: $STATUS"
  if [ "$STATUS" = "RUNNING" ]; then
    break
  fi
  sleep 10
done

echo "✅ Kafka service is RUNNING."

echo "📥 Downloading Kafka client certificates for user avnadmin..."
mkdir -p "$DEST_DIR"

avn service user-creds-download --project "$PROJECT" --username avnadmin -d "$DEST_DIR" "$SERVICE_NAME" 

echo "✅ Certificates downloaded to $DEST_DIR"

echo "📝 Writing Terraform outputs to $ENV_FILE..."

cat > "$ENV_FILE" <<EOF
# Auto-generated .env file

# Kafka Connection
KAFKA_SERVICE_URI=$(terraform output -raw kafka_service_uri)
KAFKA_HOST=$(terraform output -raw kafka_host)
KAFKA_PORT=$(terraform output -raw kafka_port)
KAFKA_PASSWORD=$(terraform output -raw kafka_password)
KAFKA_CA_CERT_PATH=$DEST_DIR/ca.pem
KAFKA_CLIENT_CERT_PATH=$DEST_DIR/service.cert
KAFKA_CLIENT_KEY_PATH=$DEST_DIR/service.key
KAFKA_USERNAME=avnadmin
KAFKA_TOPIC_NAME=clickstream_events

# PostgreSQL Connection
PG_SERVICE_URI=$(terraform output -raw pg_service_uri)
PG_HOST=$(terraform output -raw pg_host)
PG_PORT=$(terraform output -raw pg_port)
PG_USER=$(terraform output -raw pg_user)
PG_PASSWORD=$(terraform output -raw pg_password)

# OpenSearch Connection
OS_SERVICE_URI=$(terraform output -raw os_service_uri)
OS_HOST=$(terraform output -raw os_host)
OS_PORT=$(terraform output -raw os_port)
OS_USER=$(terraform output -raw os_user)
OS_PASSWORD=$(terraform output -raw os_password)
EOF

echo "✅ All connection details written to $ENV_FILE"
echo "Copying Avien details and certificate folder to ClickStream Producer and Consumer"

cp -rf .env ../clickstream_producer/
cp -rf ./certs ../clickstream_producer/
cp -rf .env ../clickstream_consumer/
cp -rf ./certs ../clickstream_consumer/

echo "Script Completed..."

