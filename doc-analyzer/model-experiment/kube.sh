#!/bin/bash

KUBE_NAMESPACE="mse-doc-classifier"
AWS_SECRET_NAME="aws-credentials"
LS_SECRET_NAME="ls-api-token"
CNTR_REG=ghcr.io
DOCKER_DWNLD_IMG_TAG=$(grep '^DOWNLOAD=' .version | cut -d'=' -f2)
DOCKER_DWNLD_IMG_NAME=classifier-downloader
DOCKER_TRAIN_IMG_TAG=$(grep '^TRAIN=' .version | cut -d'=' -f2)
DOCKER_TRAIN_IMG_NAME=classifier-train
K8S_DIR="kubernetes"

if [[ -z "$GIT_USER" || -z "$GIT_REG_TOKEN" ]]; then
    source secrets/github
    if [[ -z "$GIT_USER" || -z "$GIT_REG_TOKEN" ]]; then
        echo "GIT_USER or GIT_REG_TOKEN is empty. Please set these variables before running this script."
        exit 1
    fi
fi

function get_current_verion {
    local image_name="$1"
    local input_yaml="$2"
    grep "$image_name:" "$input_yaml" | sed "s|.*$image_name:\(.*\)|\1|"
}

function check_version {
    local new_version="$1"
    local image_name=$CNTR_REG/$GIT_USER/"$2"
    local input_yaml="$K8S_DIR/$2/job.yml"
    local job_yml_version=$(get_current_verion "$image_name" "$input_yaml")
    if [[ "$job_yml_version" != "$new_version" ]]; then
        echo "The version number has changed :" 
        printf "\t-Version in job.yml : %s\n" "$job_yml_version"
        printf "\t-Version in .version file: %s\n" "$new_version"
        read -p "Do you want to update the job with the new version? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            # Update the image key with the new version number using the image name variable
            sed "s|\(image: $image_name:\).*|\1$new_version|" $input_yaml > $input_yaml
            echo "Updated job YAML with version $new_version"
        else
            echo "Update canceled."
        fi
        exit 0
    fi
}

check_version "$DOCKER_DWNLD_IMG_TAG" "$DOCKER_DWNLD_IMG_NAME"
check_version "$DOCKER_TRAIN_IMG_TAG" "$DOCKER_TRAIN_IMG_NAME"

kubectl config set-context --current --namespace="$KUBE_NAMESPACE" > /dev/null

function status {
    kubectl get pods 
}

function push_docker_img() {
    
    local image_name="$1"
    local docker_img_tag="$2"
    echo "Docker image tag: $docker_img_tag"
    echo "Registry: $CNTR_REG"
    echo "Registry User: $GIT_USER"
    if [[ $3 == "cuda" ]]; then
        echo "$CNTR_REG/$GIT_USER/$image_name:$docker_img_tag"
        if ! docker build -t "$image_name:$docker_img_tag" -f docker/$image_name/CUDA.Dockerfile .
        then
            echo "Docker build failed. Exiting script."
            exit 1
        fi
        docker tag $image_name:$docker_img_tag $CNTR_REG/$GIT_USER/$image_name:$docker_img_tag-cuda
        docker push $CNTR_REG/$GIT_USER/$image_name:$docker_img_tag-cuda
        docker tag $image_name:$docker_img_tag $CNTR_REG/$GIT_USER/$image_name:latest-cuda
        docker push $CNTR_REG/$GIT_USER/$image_name:latest-cuda
    else
        echo "$CNTR_REG/$GIT_USER/$image_name:$docker_img_tag"
        if ! docker build -t "$image_name:$docker_img_tag" -f docker/$image_name/Dockerfile .
        then
            echo "Docker build failed. Exiting script."
            exit 1
        fi
        docker tag $image_name:$docker_img_tag $CNTR_REG/$GIT_USER/$image_name:$docker_img_tag
        docker push $CNTR_REG/$GIT_USER/$image_name:$docker_img_tag
        docker tag $image_name:$docker_img_tag $CNTR_REG/$GIT_USER/$image_name:latest
        docker push $CNTR_REG/$GIT_USER/$image_name:latest
    fi
}

function secret_exists {
    kubectl get secret $1 > /dev/null 2>&1
}

function setup {
    kubectl create secret generic $AWS_SECRET_NAME  \
        --from-file=secrets/.aws/config
    kubectl create secret generic $LS_SECRET_NAME  \
        --from-file=secrets/.lstudio/api-token
    kubectl create -f secrets/mlflow-credentials.yml
    kubectl create -f $K8S_DIR/shared/configmap.yml
    kubectl create -f $K8S_DIR/$DOCKER_TRAIN_IMG_NAME/configmap.yml
    if [[ $(kubectl config current-context) == "minikube" ]]; then
        kubectl apply -f $K8S_DIR/shared/minikube-volume.yml
    else
        kubectl apply -f $K8S_DIR/shared/volume.yml
    fi

    if [[ -z "$GIT_USER" || -z "$GIT_REG_TOKEN" ]]; then
        echo "One or more required variables are empty"
        exit 1
    fi

    kubectl create secret docker-registry ghcr-secret --docker-server=ghcr.io --docker-username=$GIT_USER --docker-password=$GIT_REG_TOKEN
}

function check_job_status {
    local job_name="$1"
    while true; do
        local status=$(kubectl get job "$job_name" -o jsonpath='{.status.conditions[?(@.type=="Complete")].status}')
        if [[ "$status" == "True" ]]; then
            echo "Job $job_name completed successfully."
            break
        fi
        sleep 5
    done
}

function job_run {
    if ! kubectl apply -f $K8S_DIR/$1/job.yml 
    then
        echo "Try to delete the existing job with ./kube.sh <job>:delete and try again."
        exit 1
    fi
}

function job_delete {
    kubectl delete -f $K8S_DIR/$1/job.yml
}

function downloader_run {
    job_run $DOCKER_DWNLD_IMG_NAME
}

function downloader_delete {
    job_delete $DOCKER_DWNLD_IMG_NAME
}

function trainer_run {
    job_run $DOCKER_TRAIN_IMG_NAME
}

function trainer_delete {
    job_delete $DOCKER_TRAIN_IMG_NAME
}


function push_docker_img_downloader {
    push_docker_img "$DOCKER_DWNLD_IMG_NAME" "$DOCKER_DWNLD_IMG_TAG"
}

function push_docker_img_trainer {
    push_docker_img "$DOCKER_TRAIN_IMG_NAME" "$DOCKER_TRAIN_IMG_TAG"
}

function push_docker_img_trainer_cuda {
    push_docker_img "$DOCKER_TRAIN_IMG_NAME" "$DOCKER_TRAIN_IMG_TAG" cuda
}

function docker_login {
    read -r -p "GitHub Username: " GITHUB_USERNAME
    read -r -s -p "GitHub Password: " GITHUB_PASSWORD
    echo "$GITHUB_PASSWORD" | docker login ghcr.io -u "$GITHUB_USERNAME" --password-stdin
    export GIT_USER=$GITHUB_USERNAME
    export GIT_REG_TOKEN=$GITHUB_PASSWORD
}

while true; do
    case "$1" in
        status)
            status
            break
            ;;
        setup)
            setup
            break
            ;;
        download:run)
            downloader_run
            break
            ;;
        download:push)
            push_docker_img_downloader
            break
            ;;
        train:push)
            push_docker_img_trainer
            break
            ;;
        train:push-cuda)
            push_docker_img_trainer_cuda
            break
            ;;
        train:run)
            trainer_run
            break
            ;;
        train:delete)
            trainer_delete
            break
            ;;
        train:status)
            check_job_status br2-$DOCKER_TRAIN_IMG_NAME
            break
            ;;
        docker:login)
            docker_login
            break
            ;;
        *)
            echo "Usage: $0 [status|setup|downloader:run|downloader:push|trainer:push|trainer:push-cuda|docker:login]"
            break
            ;;
    esac
done

echo "Current namespace is $(kubectl config view --minify --output 'jsonpath={..namespace}')"

