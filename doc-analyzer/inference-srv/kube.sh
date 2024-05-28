#!/bin/bash

KUBE_NAMESPACE="br2-doc-classifier-1"
DOCKER_IMG_TAG=${DOCKER_IMG_TAG:-v0.2}
INFERENCE_DOCKER_IMG="superjeffcplusplus/inference-service"

kubectl config set-context --current --namespace="$KUBE_NAMESPACE"

function status {
    kubectl get pods 
}

function docker_push {
    

    if ! docker build -t $INFERENCE_DOCKER_IMG:$DOCKER_IMG_TAG -f docker/Dockerfile . ; then
        echo "Failed to build docker image"
        exit 1
    fi

    docker tag $INFERENCE_DOCKER_IMG:$DOCKER_IMG_TAG ghcr.io/$INFERENCE_DOCKER_IMG:$DOCKER_IMG_TAG
    docker push ghcr.io/$INFERENCE_DOCKER_IMG:$DOCKER_IMG_TAG

    docker tag $INFERENCE_DOCKER_IMG:$DOCKER_IMG_TAG ghcr.io/$INFERENCE_DOCKER_IMG:latest
    docker push ghcr.io/$INFERENCE_DOCKER_IMG:latest

}

function deploy_inference {
    kubectl apply -f kubernetes/deployment.yml
    kubectl apply -f kubernetes/service.yml
    kubectl apply -f kubernetes/ingress.yml
}

function teardown_inference {
    kubectl delete -f kubernetes/deployment.yml
    kubectl delete -f kubernetes/service.yml
}

if [ "$1" == "status" ]; then
    status
elif [ "$1" == "docker:push" ]; then
    docker_push
elif [ "$1" == "deploy" ]; then
    deploy_inference
elif [ "$1" == "teardown" ]; then
    teardown_inference
else
    echo "Usage: $0 [status|setup|deploy|teardown]"
fi

echo "Current namespace is $(kubectl config view --minify --output 'jsonpath={..namespace}')"
