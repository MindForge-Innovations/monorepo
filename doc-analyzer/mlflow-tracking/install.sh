#!/bin/bash

KUBE_NAMESPACE="br2-mlflow"

HELM_VALUES_FILE="kubernetes/values.yaml"
RELEASE_NAME="mlflow"
CHART_PATH="./kubernetes/helm"

HOSTNAME=br2-mlflow.kube.isc.heia-fr.ch

kubectl config set-context --current --namespace=$KUBE_NAMESPACE

if [ "$1" == "uninstall" ]; then
  helm uninstall $RELEASE_NAME
  echo "If you want to restart from ZERO, don't forget to delete the persistent volume claim."
  echo "If you want to delete the persistent volume, you can run the following command:"
  echo "kubectl delete pvc -l app.kubernetes.io/instance=$RELEASE_NAME"
  exit 0
elif [ "$1" == "upgrade" ]; then
  # When upgrading, we need to get the password from the secrets
  TRACKING_AUTH_PASSWORD=$(kubectl get secret $RELEASE_NAME-tracking -o jsonpath="{.data.admin-password}" | base64 --decode)
  PG_PASSWORD=$(kubectl get secret $RELEASE_NAME-postgresql -o jsonpath="{.data.postgres-password}" | base64 --decode)
  HOSTNAME=$(kubectl get ingress $RELEASE_NAME-tracking -o jsonpath="{.spec.rules[0].host}")
  if [ -z "$TRACKING_AUTH_PASSWORD" ]; then
    echo "TRACKING_AUTH_PASSWORD is not set"
    exit 1
  fi
  if [ -z "$PG_PASSWORD" ]; then
    echo "PG_PASSWORD is not set"
    exit 1
  fi
  helm upgrade $RELEASE_NAME $CHART_PATH \
      --values $HELM_VALUES_FILE \
      --set tracking.auth.password="$TRACKING_AUTH_PASSWORD" \
      --set postgresql.auth.password="$PG_PASSWORD" \
      --set tracking.ingress.hostname="$HOSTNAME"
  exit 0
elif [ "$1" == "install" ]; then
  helm install $RELEASE_NAME $CHART_PATH \
      --values $HELM_VALUES_FILE \
      --set tracking.ingress.hostname="$HOSTNAME"
  exit 0
elif [ "$1" == "status" ]; then
  helm status $RELEASE_NAME
  exit 0
else
  echo "Usage: $0 [install|upgrade|uninstall|status]"
fi

echo "INFO : kubectl current namespace set to $KUBE_NAMESPACE"