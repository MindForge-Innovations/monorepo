#!/bin/bash

KUBE_NAMESPACE="br2-doc-analyzer-3"

HELM_VALUES_FILE="kubernetes/helm/values.yaml"
RELEASE_NAME="mlflow-tracking"
CHART_NAME="oci://registry-1.docker.io/bitnamicharts/mlflow"

# Create namespace if not exists
kubectl get namespace $KUBE_NAMESPACE 2>/dev/null ||
kubectl create namespace $KUBE_NAMESPACE

# Add Bitnami Helm repository if not exists
helm repo list | grep bitnami ||
helm repo add bitnami https://charts.bitnami.com/bitnami

if [ "$1" == "uninstall" ]; then
  helm uninstall $RELEASE_NAME --namespace $KUBE_NAMESPACE
  exit 0
elif [ "$1" == "upgrade" ]; then
  helm upgrade $RELEASE_NAME $CHART_NAME --namespace $KUBE_NAMESPACE --values $HELM_VALUES_FILE
  exit 0
else
  helm install $RELEASE_NAME $CHART_NAME --namespace $KUBE_NAMESPACE --values $HELM_VALUES_FILE
  exit 0
fi