
# Document Analyzer Model Development

This folder contains the code to train and deploy our document analysis model. It consists of tree modules: the downloader, the trainer, and the inference service. The code for these tree components is located in the `src` folder. The `docker` and `kubernetes` folders contain the necessary files to pack the code into docker images and deploy it on Kubernetes.

## Deployment

The script `kube.sh` should help you to understand how to train and deploy the model. It contains all necessary commands.

### Model training

1. Create all secrets file needed (see the `secrets` section of this README)
2. Login into the GitHub container registry : `docker login`
3. `./kube.sh setup`
4. `./kube.sh download:push`
5. `./kube.sh train:push`
6. `./kube.sh download:run`
7. `./kube.sh train:run`

### Inference service

There are currently no commands to deploy easily deploy the inference service. 

### Secrets

You must create a `secrets` directory with the following structure :

```
.
├── .aws
│   └── config
├── .lstudio
│   └── api-token
├── github
└── mlflow-credentials.yml
```
Files content :

- `.aws/config`:
```
[default]
region=<region>
aws_access_key_id=YOUR_ACCESS_KEY_ID
aws_secret_access_key=YOUR_SECRET_ACCESS_KEY
```
- `.lstudio/api-token`
```
<TOKEN>
```
- `github`
```
GIT_REG_TOKEN=<secret_token>
GIT_USER=<username>
```
- `mlflow-credentials.yml`  : See `doc-analyzer/mlflow-tracking/README.md` the values for `username` and `password`.
```yml
apiVersion: v1
kind: Secret
metadata:
  name: mlflow-basic-auth
type: kubernetes.io/basic-auth
stringData:
  username: <username> # required field for kubernetes.io/basic-auth
  password: <password> # required field for kubernetes.io/basic-auth
```

## Python local setup
1. Create a python virtual environment with `pyhton3 -m venv .venv` and activate it.
2. The requirements.txt file was generated with `pip-tools` (` pip install pip-tools`)
 - Use the command `pip-compile requirements.in` to regenerate the `requirements.txt` file with the latest version available for the project-required python packages.

