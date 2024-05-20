#!/bin/bash

KUBE_NAMESPACE="br2-doc-analyzer-0"
AWS_SECRET_NAME="aws-credentials"
LS_SECRET_NAME="ls-api-token"

function status {
    kubectl get pods -n $KUBE_NAMESPACE
}

function setup {
    kubectl create secret generic $AWS_SECRET_NAME -n $KUBE_NAMESPACE \
        --from-file=secrets/.aws/config
    kubectl create secret generic $LS_SECRET_NAME -n $KUBE_NAMESPACE \
        --from-file=secrets/.lstudio/api-token
    kubectl create -n $KUBE_NAMESPACE \
        -f kubernetes/configmap.yml
    kubectl apply -n $KUBE_NAMESPACE -f kubernetes/volume.yml
}

function apply {
    kubectl apply -n $KUBE_NAMESPACE -f kubernetes/deployment.yml
}


function teardown {
    kubectl delete -n $KUBE_NAMESPACE -f kubernetes/deployment.yml
    kubectl delete -n $KUBE_NAMESPACE -f kubernetes/volume.yml
    kubectl delete -n $KUBE_NAMESPACE -f kubernetes/configmap.yml
    kubectl delete secret $AWS_SECRET_NAME -n $KUBE_NAMESPACE
    kubectl delete secret $LS_SECRET_NAME -n $KUBE_NAMESPACE
}

if ! kubectl get namespace $KUBE_NAMESPACE 2>/dev/null; then
    echo "Create namespace $KUBE_NAMESPACE before executing this script"
    exit 1
fi

if [ "$1" == "status" ]; then
    status
elif [ "$1" == "setup" ]; then
    setup
elif [ "$1" == "apply" ]; then
    apply
elif [ "$1" == "teardown" ]; then
    teardown
else
    echo "Usage: $0 [status|setup]"
    exit 1
fi

