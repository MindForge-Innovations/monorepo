# src/main.py
import logging
from fastapi import FastAPI, UploadFile, File, Query
import torch
from torchvision import transforms
from PIL import Image
import io
import mlflow
from mlflow.tracking import MlflowClient

# ~~~ Configuration du logger ~~~

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()
client = MlflowClient()
model_name = "document_classifier"

STATUS = {"model": False}

# try:
#     model = torch.jit.load("model.pt") 
#     model.eval()
#     logging.info('Model loaded')
#     STATUS["model"] = True
# except Exception as e:
#     logging.error('Error loading model: %s', e)
#     model = None

# Transformer les données d'entrée pour le modèle
preprocess = transforms.Compose([
    transforms.Resize((240, 240)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

STATUS = {"model": False}

@app.get("/status")
async def status():
    return STATUS

@app.get("/versions")
async def list_versions():
    versions = client.get_registered_model(model_name).latest_versions
    version_info = [
        {
            "version": version.version,
            "run_id": version.run_id,
            "current_stage": version.current_stage,
            "creation_timestamp": version.creation_timestamp,
            "last_updated_timestamp": version.last_updated_timestamp
        }
        for version in versions
    ]
    return {"versions": version_info}

def load_model(path):
    try:
        model = mlflow.pytorch.load_model(path)
        model.eval()
        logging.info(f'Model version {path} loaded')
        STATUS["model"] = True
        return model
    except Exception as e:
        logging.error('Error loading model: %s', e)
        STATUS["model"] = False
        return None
    
model = load_model("/models/document-classifier-v1")

@app.post("/predict/")
async def predict(file: UploadFile = File(...), version: int = Query(...)):
    if not STATUS["model"]:
        return {"error": "Model not loaded"}
    if not model:
        return {"error": "Model not loaded"}
    image = Image.open(io.BytesIO(await file.read())).convert("RGB")
    input_tensor = preprocess(image)
    input_batch = input_tensor.unsqueeze(0)

    with torch.no_grad():
        output = model(input_batch).squeeze(1)
        prob = torch.sigmoid(output)

    return {"prediction": prob.item(), "label": int(prob > 0.5)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
