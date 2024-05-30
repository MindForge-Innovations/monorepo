# Here are some commands that can be useful but not documented in the README.md file

curl -X POST "http://doc-classifier.kube.isc.heia-fr.ch/predict/" -F "file=@data/Grotius_Dg-012.png"

curl -X POST "http://localhost:8080/predictions/document_classifier" -T data/Grotius_Dg-012.png


torch-model-archiver --model-name doc-classifier --version 0.1 --serialized-file src/model.pt

torch-model-archiver --model-name document_classifier \
                     --version 1.0 \
                     --model-file src/model.pt \
                     --serialized-file src/model.pt \
                     --handler image_classifier \
                     --export-path . \
                     --extra-files src/config/model-config.json
docker run -p 8080:80 -e MLFLOW_TRACKING_URI=$MLFLOW_TRACKING_URI -e MLFLOW_TRACKING_USERNAME=$MLFLOW_TRACKING_USERNAME -e MLFLOW_TRACKING_PASSWORD=$MLFLOW_TRACKING_PASSWORD document-classifier:test
