
# Object Detection Project

Ce qui manque:
- Création de releases sur GitHub
- CD/CI sur GitHub, automatisation
- 

## Deployment

### Steps
1. Create all secrets file needed (see the `secrets` section of this README)
2. Login into the GitHub docker regitry
   `docker login`
3. `./kube.sh setup`
4. `./kube.sh download:push`
5. `./kube.sh train:push`
6. `./kube.sh download:run`
7. `./kube.sh train:run`
8. 
### Secrets

You must create a `secrets` directory with the following structure :

```
secrets
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




```
object_detection_project/
│
├── data/                      # Dossier pour les données et scripts de préparation des données
│   ├── raw/                   # Données brutes, non modifiées
│   ├── processed/             # Données traitées et prêtes à être utilisées
│   └── dataloader.py          # Script pour charger les données
│
├── models/                    # Dossier pour les modèles, y compris les définitions et les poids
│   ├── model.py               # Définition du modèle d'object detection
│   └── weights/               # Dossier pour stocker les poids entraînés
│
├── utils/                     # Fonctions utilitaires et modules supplémentaires
│   ├── transforms.py          # Transformations de données spécifiques au projet
│   └── utilities.py           # Autres fonctions utilitaires
│
├── configs/                   # Fichiers de configuration pour gérer les hyperparamètres, etc.
│   └── config.yaml            # Fichier de configuration pour stocker les hyperparamètres
│
├── lightning_modules/         # Modules PyTorch Lightning (LightningModule, LightningDataModule)
│   ├── object_detector.py     # LightningModule pour l'entraînement du modèle
│   └── data_module.py         # LightningDataModule pour la gestion des données
│
├── experiments/               # Dossier pour stocker les logs et résultats des expériences
│   ├── logs/                  # Logs générés par TensorBoard ou un autre logger
│   └── checkpoints/           # Checkpoints de modèle sauvegardés pendant l'entraînement
│
├── notebooks/                 # Jupyter notebooks pour l'expérimentation et les démonstrations
│
├── scripts/                   # Scripts pour l'entraînement, le test, etc.
│   ├── train.py               # Script pour lancer l'entraînement
│   └── evaluate.py            # Script pour évaluer le modèle entraîné
│
└── README.md                  # Un fichier README pour expliquer le projet, l'installation, etc.
```
- **data/**: Contient toutes les données nécessaires pour le projet. Les sous-dossiers raw et processed aident à distinguer entre les données brutes et celles qui ont été prétraitées.
- **models/**: Contient les définitions des modèles ainsi que les poids après l'entraînement.
- **utils/**: Contient des scripts d'utilitaires qui peuvent être utilisés à divers endroits du projet.
- **configs/**: Contient les fichiers de configuration, ce qui facilite la gestion des différentes configurations sans modifier le code.
- **lightning_modules/**: Contient les modules spécifiques à PyTorch Lightning, séparant la logique des données de celle du modèle.
- **experiments/**: Un endroit pour stocker les résultats et les logs des expériences pour faciliter l'analyse et la reproduction.
- **notebooks/**: Contient des notebooks Jupyter pour des expérimentations rapides ou des démonstrations.
- **scripts/**: Contient des scripts pour exécuter des tâches courantes comme l'entraînement et l'évaluation.
