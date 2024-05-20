#!/bin/bash

KUBE_NAMESPACE="br2-doc-analyzer-0"

HELM_VALUES_FILE="kubernetes/values.yaml"
RELEASE_NAME="mlflow-tracking"
CHART_NAME="./kubernetes/helm"

HOSTNAME=msemlflow.kube.isc.heia-fr.ch
HOSTNAME=$(kubectl get ingress --namespace $KUBE_NAMESPACE $RELEASE_NAME-tracking -o jsonpath="{.spec.rules[0].host}")

if ! kubectl get namespace $KUBE_NAMESPACE 2>/dev/null; then
  echo "Create namespace $KUBE_NAMESPACE before executing this script"
  exit 1
fi

helm repo list | grep bitnami 2>/dev/null ||
helm repo add bitnami https://charts.bitnami.com/bitnami

if [ "$1" == "uninstall" ]; then
  helm uninstall $RELEASE_NAME --namespace $KUBE_NAMESPACE
  exit 0
elif [ "$1" == "upgrade" ]; then
  # When upgrading, we need to get the password from the secrets
  TRACKING_AUTH_PASSWORD=$(kubectl get secret --namespace  $KUBE_NAMESPACE $RELEASE_NAME-tracking -o jsonpath="{.data.admin-password}" | base64 --decode)
  PG_PASSWORD=$(kubectl get secret --namespace  $KUBE_NAMESPACE $RELEASE_NAME-postgresql -o jsonpath="{.data.postgres-password}" | base64 --decode)
  HOSTNAME=$(kubectl get ingress --namespace br2-doc-analyzer-0 mlflow-tracking-tracking -o jsonpath="{.spec.rules[0].host}")
  if [ -z "$TRACKING_AUTH_PASSWORD" ]; then
    echo "TRACKING_AUTH_PASSWORD is not set"
    exit 1
  fi
  if [ -z "$PG_PASSWORD" ]; then
    echo "PG_PASSWORD is not set"
    exit 1
  fi
  helm upgrade $RELEASE_NAME $CHART_NAME \
      --namespace $KUBE_NAMESPACE \
      --values $HELM_VALUES_FILE \
      --set tracking.auth.password="$TRACKING_AUTH_PASSWORD" \
      --set postgresql.auth.password="$PG_PASSWORD" \
      --set tracking.ingress.hostname="$HOSTNAME"
  exit 0
elif [ "$1" == "install" ]; then
  helm install $RELEASE_NAME $CHART_NAME --namespace $KUBE_NAMESPACE --values $HELM_VALUES_FILE
  exit 0
elif [ "$1" == "status" ]; then
  helm status $RELEASE_NAME --namespace $KUBE_NAMESPACE
  exit 0
else
  echo "Usage: $0 [install|upgrade|uninstall|status]"
  exit 1
fi