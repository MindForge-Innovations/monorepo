#!/bin/bash

KUBE_NAMESPACE="br2-doc-analyzer-1"

HELM_VALUES_FILE="kubernetes/helm/values.yaml"
RELEASE_NAME="pg-mlflow"
CHART_NAME="oci://registry-1.docker.io/bitnamicharts/postgresql"

if ! kubectl get namespace $KUBE_NAMESPACE 2>/dev/null; then
  echo "Create namespace $KUBE_NAMESPACE before executing this script"
  exit 1
fi

helm repo list | grep bitnami ||
helm repo add bitnami https://charts.bitnami.com/bitnami

if [ "$1" == "uninstall" ]; then
  helm uninstall $RELEASE_NAME --namespace $KUBE_NAMESPACE
  exit 0
elif [ "$1" == "upgrade" ]; then
  check if the password is set
  if [ -z "$PGSQL_AUTH_PASSWORD" ]; then
    echo "PGSQL_AUTH_PASSWORD is not set"
    exit 1
  fi
  helm upgrade $RELEASE_NAME $CHART_NAME \
      --namespace $KUBE_NAMESPACE \
      --values $HELM_VALUES_FILE \
    #   --set global.postgresql.auth.password="$PGSQL_AUTH_PASSWORD"
      # --set tracking.auth.password="$TRACKING_AUTH_PASSWORD"
  exit 0
else
  helm install $RELEASE_NAME $CHART_NAME --namespace $KUBE_NAMESPACE --values $HELM_VALUES_FILE
  exit 0
fi