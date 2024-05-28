# src/main.py
import logging
from fastapi import FastAPI, UploadFile, File
import torch
from torchvision import transforms
from PIL import Image
import io

# ~~~ Configuration du logger ~~~

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

STATUS = {"model": False}

try:
    model = torch.jit.load("model.pt") 
    model.eval()
    logging.info('Model loaded')
    STATUS["model"] = True
except Exception as e:
    logging.error('Error loading model: %s', e)
    model = None

# Transformer les données d'entrée pour le modèle
preprocess = transforms.Compose([
    transforms.Resize((240, 240)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])



@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    if not STATUS["model"]:
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
