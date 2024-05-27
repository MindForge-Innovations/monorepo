#!/bin/bash

KUBE_NAMESPACE="br2-doc-classifier"
AWS_SECRET_NAME="aws-credentials"
LS_SECRET_NAME="ls-api-token"
REGISTRY=ghcr.io
DOCKER_IMG_TAG=${DOCKER_IMG_TAG:-v0.2}

# if ! kubectl get namespace $KUBE_NAMESPACE 2>/dev/null; then
#     echo "Create namespace $KUBE_NAMESPACE before executing this script"
#     exit 1
# fi

kubectl config set-context --current --namespace="$KUBE_NAMESPACE"

function status {
    kubectl get pods 
}

function setup {
    kubectl create secret generic $AWS_SECRET_NAME  \
        --from-file=secrets/.aws/config
    kubectl create secret generic $LS_SECRET_NAME  \
        --from-file=secrets/.lstudio/api-token
    kubectl create  \
        -f kubernetes/configmap.yml
    if [[ $(kubectl config current-context) == "minikube" ]]; then
        kubectl apply -f kubernetes/minikube-volume.yml
    else
        kubectl apply -f kubernetes/volume.yml
    fi

    if [[ -z "$GIT_USER" || -z "$GIT_REG_TOKEN" ]]; then
        echo "One or more required variables are empty"
        exit 1
    fi

    kubectl create secret docker-registry ghcr-secret --docker-server=ghcr.io --docker-username=$GIT_USER --docker-password=$GIT_REG_TOKEN

}

function apply {
    kubectl apply  -f kubernetes/deployment.yml
}

function downloader_run {
    kubectl apply -f kubernetes/downloader-job.yml
}

function push_docker_images {
    echo "Docker image tag: $DOCKER_IMG_TAG"
    echo "Registry: $REGISTRY"
    echo Registry User: $GIT_USER
    echo $REGISTRY/$GIT_USER/downloader:"$DOCKER_IMG_TAG"
    docker build -t "downloader:$DOCKER_IMG_TAG" -f docker/downloader/Dockerfile .
    docker tag "downloader:$DOCKER_IMG_TAG" "$REGISTRY"/"$GIT_USER"/downloader:"$DOCKER_IMG_TAG"
    docker push "$REGISTRY/$GIT_USER/downloader:$DOCKER_IMG_TAG"
    docker tag "downloader:$DOCKER_IMG_TAG" "$REGISTRY"/"$GIT_USER"/downloader:latest
    docker push "$REGISTRY/$GIT_USER/downloader:latest"
}

function teardown {
    kubectl delete  -f kubernetes/deployment.yml
    kubectl delete  -f kubernetes/volume.yml
    kubectl delete  -f kubernetes/configmap.yml
    kubectl delete secret $AWS_SECRET_NAME 
    kubectl delete secret $LS_SECRET_NAME 
}

if [ "$1" == "status" ]; then
    status
elif [ "$1" == "setup" ]; then
    setup
elif [ "$1" == "downloader:run" ]; then
    apply
elif [ "$1" == "teardown" ]; then
    teardown
elif [ "$1" == "docker:push" ]; then
    push_docker_images
elif [ "$1" == "docker:login" ]; then
    read -r -p "GitHub Username: " GITHUB_USERNAME
    read -r -s -p "GitHub Password: " GITHUB_PASSWORD
    echo "$GITHUB_PASSWORD" | docker login ghcr.io -u "$GITHUB_USERNAME" --password-stdin
    export GIT_USER=$GITHUB_USERNAME
    export GIT_REG_TOKEN=$GITHUB_PASSWORD
    echo "To make other commands work, please ensure that GIT_USER and GIT_REG_TOKEN environment variables are set."
else
    echo "Usage: $0 [status|setup]"
fi

echo "Current namespace is $(kubectl config view --minify --output 'jsonpath={..namespace}')"

